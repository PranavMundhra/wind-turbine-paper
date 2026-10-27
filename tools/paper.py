#!/usr/bin/env python3
"""paper.py: the grounding toolbelt for a co-written LaTeX paper.

Everything Claude needs to stay grounded is answered from disk by this script, so the
conversation never has to hold whole PDFs, notebooks or sections:

  status                      session start: STATE.md + one-line health summary
  para <id> [--snapshot]      print one paragraph (and snapshot a Claude draft)
  evidence <ref>              experiment status / run metrics from the code repo
  search <query> [-k N]       full-text search over approved cards + ingested pages
  page <key> <n>              one page of an ingested paper (to verify a quote)
  find <query> [-n N]         Semantic Scholar search (only after the user agrees)
  add-doi <doi> [--key K]     verified metadata from Crossref -> refs/inbox/<key>.md
  add-arxiv <id> [--key K]    verified metadata from arXiv     -> refs/inbox/<key>.md
  add-pdf <pdf...>            read DOI/arXiv id from each PDF, verify, make inbox card, ingest text
  ingest <pdf> --key K        pdf -> refs/text/<key>.txt with page markers
  cards [--verify]            list cards; --verify string-matches every quote
  approve <key> / reject <key> --reason R   (run only on the user's say-so)
  bib                         regenerate refs/library.bib from approved cards
  check [files...]            lint the draft: cites, provenance, numbers, status, slop
  style-diff [--accept]       how humans changed Claude's drafts (to update style.md)
  init <dir> --code-repo P    scaffold a new paper repo

Only the standard library + PyYAML. Network is used by add-doi, add-arxiv and find only.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("paper.py needs PyYAML: pip install pyyaml")


# Windows defaults to cp1252; paper text and cards are UTF-8.
_rt, _wt = Path.read_text, Path.write_text
Path.read_text = lambda self, encoding="utf-8", errors=None: _rt(self, encoding=encoding, errors=errors)
Path.write_text = lambda self, data, encoding="utf-8", errors=None, newline=None: _wt(self, data, encoding=encoding, errors=errors, newline=newline)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

HERE = Path(__file__).resolve().parent
UA = "paper.py (grounded-paper skill; mailto:unknown)"

# --------------------------------------------------------------------------- config

def find_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for d in [p, *p.parents]:
        if (d / ".paper" / "config.yaml").exists():
            return d
    sys.exit("Not inside a paper repo (no .paper/config.yaml). Run `paper.py init` first.")


def load_cfg(root: Path) -> dict:
    cfg = yaml.safe_load((root / ".paper" / "config.yaml").read_text()) or {}
    code = os.environ.get("PAPER_CODE_REPO") or cfg.get("code_repo", "../code")
    cfg["code_repo_path"] = (root / code).resolve() if not Path(code).is_absolute() else Path(code)
    cfg.setdefault("registry", "experiments/registry.yaml")
    cfg.setdefault("evidence_roots", ["results/runs", "results/evidence"])
    cfg.setdefault("run_files", ["results.json", "results_display.json", "evidence.json", "manifest.json"])
    cfg.setdefault("sections_dir", "sections")
    cfg.setdefault("noise_experiment", None)
    cfg.setdefault("single_seed", False)
    cfg.setdefault("status_rules", {})
    return cfg

# --------------------------------------------------------------------------- cards

FM = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


def read_card(path: Path) -> dict:
    m = FM.match(path.read_text())
    if not m:
        raise ValueError(f"{path}: missing YAML front matter")
    d = yaml.safe_load(m.group(1)) or {}
    d["_notes"] = m.group(2)
    d["_path"] = path
    return d


def write_card(path: Path, d: dict) -> None:
    notes = d.pop("_notes", "")
    d.pop("_path", None)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100)
                    + "---\n" + (notes or ""))


def all_cards(root: Path) -> dict[str, dict]:
    out = {}
    for sub in ("cards", "inbox", "rejected"):
        for p in sorted((root / "refs" / sub).glob("*.md")):
            try:
                c = read_card(p)
            except Exception as e:  # noqa: BLE001
                print(f"WARN bad card {p}: {e}", file=sys.stderr)
                continue
            out[c.get("key", p.stem)] = c
    return out


def norm(s: str) -> str:
    s = s.replace("\u00ad", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"-\s*\n\s*", "", s)          # de-hyphenate line breaks
    s = re.sub(r"[\u2010-\u2015]", "-", s)
    s = re.sub(r"[\u2018\u2019]", "'", s)
    s = re.sub(r"[\u201c\u201d]", '"', s)
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_found(root: Path, card: dict, quote: str) -> bool:
    q = norm(quote).strip(" .\"'…")
    if not q:
        return False
    txt = root / "refs" / "text" / f"{card['key']}.txt"
    hay = norm(txt.read_text()) if txt.exists() else ""
    hay += " " + norm(str(card.get("abstract") or ""))
    if q in hay:
        return True
    # tolerate an ellipsis inside the quote: every fragment must appear, in order
    parts = [p.strip() for p in re.split(r"\.\.\.|…", q) if p.strip()]
    pos = 0
    for p in parts:
        i = hay.find(p, pos)
        if i < 0:
            return False
        pos = i + len(p)
    return bool(parts)

# --------------------------------------------------------------------------- evidence

def registry(cfg: dict) -> dict[str, dict]:
    p = cfg["code_repo_path"] / cfg["registry"]
    if not p.exists():
        return {}
    data = yaml.safe_load(p.read_text()) or {}
    items = data.get("experiments", data if isinstance(data, list) else [])
    return {str(e["id"]): e for e in items if isinstance(e, dict) and "id" in e}


def run_dirs(cfg: dict, exp: str) -> list[Path]:
    out = []
    for r in cfg["evidence_roots"]:
        d = cfg["code_repo_path"] / r / exp
        if d.is_dir():
            out += sorted(p for p in d.iterdir() if p.is_dir())
    return out


def dig(obj, key: str):
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    cur = obj
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise KeyError(key)
    return cur


def resolve_c(cfg: dict, ref: str):
    """Return (experiment_id, value_or_None, where) for a [C:...] reference.

    Forms:  EXP            experiment-level claim (no number)
            EXP@RUN:key    value from that run dir's result files
            EXP=path#key   value from any JSON file in the code repo
    """
    if "=" in ref:
        exp, rest = ref.split("=", 1)
        path, _, key = rest.partition("#")
        f = cfg["code_repo_path"] / path
        if not f.exists():
            raise LookupError(f"file not found: {path}")
        return exp, dig(json.loads(f.read_text()), key), path
    if "@" in ref:
        exp, rest = ref.split("@", 1)
        run, _, key = rest.partition(":")
        dirs = [d for d in run_dirs(cfg, exp) if d.name == run]
        if not dirs:
            raise LookupError(f"run dir not found: {exp}/{run}")
        if not key:
            return exp, None, str(dirs[0])
        for fn in cfg["run_files"]:
            f = dirs[0] / fn
            if f.exists():
                try:
                    return exp, dig(json.loads(f.read_text()), key), str(f.relative_to(cfg["code_repo_path"]))
                except KeyError:
                    continue
        raise LookupError(f"key '{key}' not in {', '.join(cfg['run_files'])} of {exp}/{run}")
    return ref, None, "registry"


def flatten(obj, prefix="", depth=0, out=None):
    """Dotted keys -> scalar values (short scalar lists kept whole), max depth 3."""
    out = {} if out is None else out
    if isinstance(obj, dict) and depth < 3:
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)):
                flatten(v, key, depth + 1, out)
            else:
                out[key] = v
    elif isinstance(obj, list) and len(obj) <= 8 and all(not isinstance(x, (dict, list)) for x in obj):
        out[prefix] = obj
    return out


def cmd_evidence(a):
    root = find_root(); cfg = load_cfg(root); reg = registry(cfg)
    ref = a.ref
    if "@" in ref or "=" in ref:
        if ":" in ref.split("@", 1)[-1] or "#" in ref:
            exp, val, where = resolve_c(cfg, ref)
            print(f"{ref} = {val!r}   ({where}; {exp} status={reg.get(exp, {}).get('status', '?')})")
            return
        exp, _, where = resolve_c(cfg, ref)
        d = Path(where)
        for fn in cfg["run_files"]:
            f = d / fn
            if f.exists() and f.stat().st_size < 200_000:
                flat = {k: v for k, v in flatten(json.loads(f.read_text())).items()
                        if not (isinstance(v, str) and (len(v) > 90 or re.fullmatch(r"[0-9a-f]{32,}", v)))}
                print(f"# {fn}")
                for k, v in flat.items():
                    print(f"  {k}: {v}")
        return
    e = reg.get(ref)
    if not e:
        sys.exit(f"{ref}: not in registry ({cfg['code_repo_path'] / cfg['registry']})")
    keep = ["id", "title", "status", "importance", "question", "depends_on", "compares_with", "doc", "config"]
    for k in keep:
        if k in e:
            print(f"{k}: {e[k]}")
    runs = run_dirs(cfg, ref)
    print(f"runs: {len(runs)}")
    for d in runs:
        summ = None
        for fn in cfg["run_files"][:2]:
            f = d / fn
            if f.exists():
                j = json.loads(f.read_text())
                summ = {k: j[k] for k in ("care", "coverage", "earliness", "reliability", "accuracy", "seed") if k in j}
                break
        print(f"  {ref}@{d.name}  {summ or '(no results file)'}")
    rule = rule_for(cfg, e.get("status"))
    if rule:
        print(f"writing rule for status '{e.get('status')}': {rule}")


DEFAULT_RULES = {
    "planned": "future work only; no results may be stated",
    "partial": "say 'preliminary'/'initial'; no final claims",
    "done-unverified": "hedge or verify first: numbers exist only in prose",
    "done": "may be stated as a result",
}


def rule_for(cfg, status):
    return {**DEFAULT_RULES, **(cfg.get("status_rules") or {})}.get(status)

# --------------------------------------------------------------------------- tex parsing

COMMENT = re.compile(r"(?<!\\)%")
MARK = re.compile(r"\[(C|L|I)(?::([^\]]+))?\]")
ANCHOR = re.compile(r"^\s*%\s*@para\s+(\S+)(.*)$")
CITE = re.compile(r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|parencite|textcite)\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")
NUM = re.compile(r"(?<![\w.\\{])(-?\d{1,3}(?:,\d{3})+|-?\d+(?:\.\d+)?)(\s*\\?%)?(?![\w}])")
STRIP_CMDS = re.compile(r"\\(?:cite\w*|ref|eqref|label|autoref|cref|Cref|input|include|includegraphics|url|href)\*?(?:\[[^\]]*\])*\{[^}]*\}")
COMPARE = re.compile(r"\b(outperform\w*|better|worse|improv\w*|higher|lower|exceed\w*|surpass\w*|beat\w*|superior|inferior|gain\w*|drop\w*)\b", re.I)
HEDGE = {"planned": re.compile(r"\b(will|plan\w*|future|intend\w*|propose\w*)\b", re.I),
         "partial": re.compile(r"\b(preliminary|initial|partial|early|so far|ongoing)\b", re.I),
         "done-unverified": re.compile(r"\b(reported|unverified|approximately|about|around|suggest\w*|indicat\w*)\b", re.I)}
# Filler that marks text as machine-written. A trailing * means "any word starting with this stem".
SINGLE_RE = re.compile(r"single[- ]seed|one seed|single run|one run|seed\s*\d+", re.I)
STRONG = re.compile(r"\b(clearly|significant\w*|substantial\w*|robust\w*|consistent\w*|conclusive\w*|demonstrat\w*|prov(?:e|es|ed|en))\b", re.I)
SLOP = ["delve*", "crucial", "pivotal", "notably", "it is important to note", "it is worth noting", "in the realm of",
        "plays a vital role", "plays a key role", "plays a crucial role", "a testament to", "navigat*", "landscape",
        "furthermore,", "moreover,", "in conclusion,", "underscore*", "seamless*", "leverag*", "robust", "novel",
        "groundbreaking", "cutting-edge", "state-of-the-art", "holistic", "intricate", "tapestry", "paradigm",
        "showcas*", "harness*", "unlock*", "comprehensive", "meticulous*", "boast*"]
SLOP_RE = [(p, re.compile(r"\b" + re.escape(p.rstrip("*")) + (r"\w*" if p.endswith("*") else r"\b"), re.I)) for p in SLOP]


def split_line(line: str):
    m = COMMENT.search(line)
    return (line[:m.start()], line[m.start() + 1:]) if m else (line, "")


def tex_files(root: Path, cfg: dict, files=None) -> list[Path]:
    if files:
        return [Path(f).resolve() for f in files]
    return sorted((root / cfg["sections_dir"]).glob("*.tex"))


def paragraphs(path: Path):
    """Yield (id, flags, start_line, lines) for each anchored paragraph."""
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        m = ANCHOR.match(lines[i])
        if m:
            start, body = i, [lines[i]]
            i += 1
            while i < len(lines) and lines[i].strip() and not ANCHOR.match(lines[i]):
                body.append(lines[i]); i += 1
            yield m.group(1), m.group(2).split(), start + 1, body
        else:
            i += 1


def cmd_para(a):
    root = find_root(); cfg = load_cfg(root)
    for f in tex_files(root, cfg):
        for pid, flags, ln, body in paragraphs(f):
            if pid == a.id:
                text = "\n".join(body)
                if a.snapshot:
                    snap = root / ".paper" / "drafts" / f"{pid}.tex"
                    snap.parent.mkdir(parents=True, exist_ok=True)
                    snap.write_text(text + "\n")
                    print(f"snapshot saved: .paper/drafts/{pid}.tex")
                else:
                    print(f"# {f.relative_to(root)}:{ln}\n{text}")
                return
    sys.exit(f"paragraph '{a.id}' not found (anchor: % @para {a.id})")

# --------------------------------------------------------------------------- check

def num_val(tok: str) -> float:
    return float(tok.replace(",", ""))


def decimals(tok: str) -> int:
    return len(tok.split(".")[1]) if "." in tok else 0


def number_matches(tok: str, pct: bool, values: list) -> bool:
    t, d = num_val(tok), decimals(tok)
    flat = []
    for v in values:  # numbers inside strings/lists ("-365 days", ['0.1', ...]) count too
        if isinstance(v, (list, tuple)):
            flat += list(v)
        else:
            flat.append(v)
    nums = []
    for v in flat:
        if isinstance(v, str):
            nums += [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*(?:\.\d+)?", v)]
        else:
            nums.append(v)
    values = nums
    for v in values:
        if isinstance(v, bool):
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        for cand in ((v, v * 100) if pct or v <= 1 else (v,)):
            if abs(cand - t) <= 0.5 * 10 ** -d + 1e-12:
                return True
    return False


def cmd_check(a):
    root = find_root(); cfg = load_cfg(root); reg = registry(cfg)
    cards = all_cards(root)
    approved = {k: c for k, c in cards.items() if c.get("status") == "approved"}
    noise = cfg.get("noise_experiment")
    noise_done = noise is None or reg.get(noise, {}).get("status") == "done"
    errs = warns = 0
    drafts = []

    def emit(level, f, ln, code, msg):
        nonlocal errs, warns
        if level == "ERROR":
            errs += 1
        else:
            warns += 1
            if a.errors_only:
                return
        print(f"{f.relative_to(root)}:{ln} {level} {code}: {msg}")

    for f in tex_files(root, cfg, a.files):
        draft_lines = set()
        for pid, flags, ln, body in paragraphs(f):
            if "draft" in flags:
                drafts.append(pid)
                draft_lines.update(range(ln, ln + len(body)))
        for ln, line in enumerate(f.read_text().splitlines(), 1):
            text, comment = split_line(line)
            if not text.strip() or text.lstrip().startswith("\\") and not re.search(r"[a-z]{3,}\s+[a-z]{3,}", STRIP_CMDS.sub("", text)):
                continue
            marks = MARK.findall(comment)
            cites = [k.strip() for g in CITE.findall(text) for k in g.split(",") if k.strip()]
            # --- citations
            for k in cites:
                if k not in approved:
                    st = cards.get(k, {}).get("status", "no card")
                    emit("ERROR", f, ln, "UNAPPROVED-CITE", f"\\cite{{{k}}} is {st}; only approved cards may be cited")
            lrefs = [r for t, r in marks if t == "L"]
            for r in lrefs:
                key, _, cid = r.partition("#")
                c = approved.get(key)
                if not c:
                    emit("ERROR", f, ln, "L-UNKNOWN", f"[L:{r}] has no approved card")
                elif cid and cid not in {str(x.get("id")) for x in c.get("claims") or []}:
                    emit("ERROR", f, ln, "L-CLAIM", f"[L:{r}] claim id not on card {key}")
                if c and key not in cites:
                    emit("WARN", f, ln, "L-NOCITE", f"[L:{r}] marker but no \\cite{{{key}}} in the sentence")
            for k in cites:
                if k in approved and not any(r.split("#")[0] == k for r in lrefs):
                    emit("WARN", f, ln, "CITE-NOCLAIM", f"\\cite{{{k}}} without [L:{k}#cN]: which claim supports this?")
            # --- experiment grounding
            values, exps = [], []
            for t, r in marks:
                if t != "C" or not r:
                    continue
                try:
                    exp, val, _ = resolve_c(cfg, r.strip())
                except (LookupError, KeyError, ValueError) as e:
                    emit("ERROR", f, ln, "C-BROKEN", f"[C:{r}] {e}")
                    continue
                exps.append(exp)
                if val is not None:
                    values.append(val)
                e = reg.get(exp)
                if not e:
                    emit("ERROR", f, ln, "C-UNKNOWN", f"experiment '{exp}' not in registry")
                    continue
                st = e.get("status")
                hedge = HEDGE.get(st)
                if st == "planned" and not hedge.search(text):
                    emit("ERROR", f, ln, "NOT-RUN", f"{exp} is planned; {rule_for(cfg, st)}")
                elif hedge and st != "planned" and not hedge.search(text):
                    emit("WARN", f, ln, st.upper(), f"{exp} is {st}; {rule_for(cfg, st)}")
            if exps and not noise_done and COMPARE.search(text) and (len(set(exps)) >= 2 or "than" in text):
                emit("WARN", f, ln, "NOISE", f"comparison before {noise} (noise/seed robustness) is done; may be within run-to-run noise")
            if cfg.get("single_seed") and exps and COMPARE.search(text):
                if not SINGLE_RE.search(text):
                    emit("WARN", f, ln, "SINGLE-SEED", "comparison must say it comes from one seed (e.g. 'in our single-seed run')")
                if STRONG.search(text):
                    emit("WARN", f, ln, "OVERCLAIM", f"'{STRONG.search(text).group(0)}' is too strong for a single-seed comparison")
            # --- numbers
            body = STRIP_CMDS.sub("", text)
            body = re.sub(r"\\(?:section|subsection|subsubsection|paragraph|caption)\*?\{[^}]*\}", "", body)
            for m in NUM.finditer(body):
                tok, pct = m.group(1), bool(m.group(2))
                n = num_val(tok)
                if not pct and "." not in tok and (abs(n) < 10 or 1900 <= n <= 2100):
                    continue  # small integers and years: too ambiguous to police
                if values:
                    if not number_matches(tok, pct, values):
                        emit("WARN", f, ln, "MISMATCH", f"{tok}{'%' if pct else ''} matches none of the referenced values {values[:4]}")
                elif lrefs:
                    quotes = " ".join(str(x.get("quote", "")) + " " + str(x.get("numbers", ""))
                                      for r in lrefs for x in (approved.get(r.split('#')[0], {}).get("claims") or [])
                                      if str(x.get("id")) == r.partition("#")[2])
                    if tok not in quotes:
                        emit("WARN", f, ln, "L-NUMBER", f"{tok} not found in the cited claim's quote/numbers")
                else:
                    emit("WARN", f, ln, "UNBACKED-NUMBER", f"{tok}{'%' if pct else ''} has no [C:...] or [L:...] source")
            # --- provenance + slop
            if not marks and len(body.split()) >= 6 and not a.lenient:
                emit("WARN", f, ln, "NO-PROVENANCE", "sentence has no [C]/[L]/[I] marker")
            if ln in draft_lines:
                for p, rx in SLOP_RE:
                    if rx.search(body):
                        emit("WARN", f, ln, "SLOP", f"'{p.rstrip('*')}' in a Claude draft")
    if cfg.get("single_seed") and not a.files:
        alltxt = " ".join(p.read_text() for p in tex_files(root, cfg))
        if any(MARK.search(split_line(l)[1]) for l in alltxt.splitlines()) and not SINGLE_RE.search(" ".join(split_line(l)[0] for l in alltxt.splitlines())):
            print("LIMITATION: results are reported but no section mentions that they come from a single seed; add it to Discussion/Limitations")
            warns += 1
    print(f"--- {errs} error(s), {warns} warning(s); {len(drafts)} paragraph(s) still marked draft"
          + (f": {', '.join(drafts[:12])}" if drafts else ""))
    sys.exit(1 if errs else 0)

# --------------------------------------------------------------------------- search index

def build_index(root: Path) -> sqlite3.Connection:
    db = root / ".paper" / "index.db"
    srcs = list((root / "refs" / "cards").glob("*.md")) + list((root / "refs" / "text").glob("*.txt"))
    newest = max((p.stat().st_mtime for p in srcs), default=0)
    fresh = db.exists() and db.stat().st_mtime >= newest
    con = sqlite3.connect(db)
    if fresh:
        return con
    con.execute("DROP TABLE IF EXISTS fts")
    con.execute("CREATE VIRTUAL TABLE fts USING fts5(kind UNINDEXED, key UNINDEXED, loc UNINDEXED, body, tokenize='porter')")
    rows = []
    for p in (root / "refs" / "cards").glob("*.md"):
        c = read_card(p)
        if c.get("status") != "approved":
            continue
        rows.append(("card", c["key"], "title", f"{c.get('title','')} {c.get('abstract','') or ''}"))
        for cl in c.get("claims") or []:
            rows.append(("claim", c["key"], f"{cl.get('id')} {cl.get('loc','')}",
                         f"{cl.get('text','')} {cl.get('quote','')} {cl.get('numbers','')}"))
    approved = {r[1] for r in rows}
    for p in (root / "refs" / "text").glob("*.txt"):
        if p.stem not in approved:
            continue
        parts = re.split(r"^=== page (\d+) ===$", p.read_text(), flags=re.M)
        for n, body in zip(parts[1::2], parts[2::2]):
            rows.append(("page", p.stem, f"p.{n}", body))
    con.executemany("INSERT INTO fts VALUES (?,?,?,?)", rows)
    con.commit()
    return con


def cmd_search(a):
    root = find_root()
    con = build_index(root)
    q = " OR ".join(f'"{w}"' for w in re.findall(r"[\w-]+", a.query) if len(w) > 2) or a.query
    rows = con.execute("SELECT kind,key,loc,snippet(fts,3,'[',']','…',14) FROM fts WHERE fts MATCH ? "
                       "ORDER BY CASE kind WHEN 'claim' THEN 0 WHEN 'card' THEN 1 ELSE 2 END, rank LIMIT ?",
                       (q, a.k)).fetchall()
    if not rows:
        print("no hits in approved library (that is a valid answer; offer a search only if the user wants one)")
    for kind, key, loc, snip in rows:
        print(f"{kind:5} {key:22} {loc:14} {' '.join(snip.split())}")


def cmd_page(a):
    root = find_root()
    t = root / "refs" / "text" / f"{a.key}.txt"
    if not t.exists():
        sys.exit(f"no text for {a.key}; ingest the PDF first")
    parts = re.split(r"^=== page (\d+) ===$", t.read_text(), flags=re.M)
    pages = dict(zip(parts[1::2], parts[2::2]))
    body = pages.get(str(a.n))
    if body is None:
        sys.exit(f"{a.key} has pages 1..{len(pages)}")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n+", "\n", body).strip()
    if a.grep:
        idx = norm(body).find(norm(a.grep))
        print(f"quote {'FOUND' if idx >= 0 else 'NOT FOUND'} on p.{a.n}")
        if idx >= 0:
            return
    print(body[: a.max_chars])

# --------------------------------------------------------------------------- refs intake

def http_get(url: str, accept: str | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def make_key(authors: list[str], year, title: str) -> str:
    sur = re.sub(r"[^a-z]", "", (authors[0].split()[-1] if authors else "anon").lower())
    stop = {"a", "an", "the", "on", "of", "for", "and", "in", "to", "with", "towards", "toward", "using"}
    word = next((w for w in re.findall(r"[A-Za-z]+", title.lower()) if w not in stop), "x")
    return f"{sur}{year or ''}{word}"


def title_ok(expected: str | None, got: str) -> bool:
    if not expected:
        return True
    return difflib.SequenceMatcher(None, norm(expected), norm(got)).ratio() >= 0.85


def new_card(root: Path, key: str, meta: dict, bibtex: str) -> Path:
    for sub in ("cards", "inbox", "rejected"):
        if (root / "refs" / sub / f"{key}.md").exists():
            sys.exit(f"{key} already exists in refs/{sub}/ (rejected papers stay rejected unless the user says otherwise)")
    bibtex = re.sub(r"^(@\w+\{)[^,]*,", rf"\g<1>{key},", bibtex.strip(), count=1)
    card = {"key": key, **meta, "verified_on": str(date.today()), "status": "candidate",
            "access": "abstract-only", "relevance": "", "claims": [], "bibtex": bibtex + "\n"}
    p = root / "refs" / "inbox" / f"{key}.md"
    card["_notes"] = "\nNotes (human or Claude): why this paper matters for *our* paper.\n"
    write_card(p, card)
    return p


def cmd_add_doi(a):
    root = find_root()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", a.doi.strip(), flags=re.I)
    try:
        msg = json.loads(http_get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"))["message"]
    except Exception as e:  # noqa: BLE001
        sys.exit(f"DOI did not resolve on Crossref ({e}). Not adding it: never construct metadata by hand.")
    title = (msg.get("title") or [""])[0]
    if not title_ok(a.expect_title, title):
        sys.exit(f"TITLE MISMATCH: Crossref says '{title}'. Not adding it.")
    authors = [f"{x.get('given','')} {x.get('family','')}".strip() for x in msg.get("author", [])]
    year = ((msg.get("issued") or {}).get("date-parts") or [[None]])[0][0]
    try:
        bib = http_get(f"https://doi.org/{doi}", "application/x-bibtex").decode()
    except Exception:  # noqa: BLE001
        bib = f"@article{{x,\n  title={{{title}}},\n  author={{{' and '.join(authors)}}},\n  year={{{year}}},\n  doi={{{doi}}}\n}}"
    abstract = re.sub(r"<[^>]+>", "", msg.get("abstract") or "").strip() or None
    meta = {"doi": doi, "title": title, "authors": authors, "year": year,
            "venue": (msg.get("container-title") or [""])[0], "verified_via": "crossref", "abstract": abstract}
    p = new_card(root, a.key or make_key(authors, year, title), meta, bib)
    print(f"candidate card: {p.relative_to(root)}\n  {title} ({year}); {', '.join(authors[:3])}{' et al.' if len(authors) > 3 else ''}")
    return p


def cmd_add_arxiv(a):
    root = find_root()
    aid = re.sub(r"^(https?://arxiv\.org/(abs|pdf)/|arxiv:)", "", a.id.strip(), flags=re.I).removesuffix(".pdf")
    try:
        xml = http_get(f"http://export.arxiv.org/api/query?id_list={aid}")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"arXiv lookup failed ({e}). Not adding it.")
    ns = {"a": "http://www.w3.org/2005/Atom"}
    ent = ET.fromstring(xml).find("a:entry", ns)
    if ent is None or ent.find("a:title", ns) is None:
        sys.exit("arXiv id did not resolve. Not adding it.")
    title = " ".join(ent.find("a:title", ns).text.split())
    if not title_ok(a.expect_title, title):
        sys.exit(f"TITLE MISMATCH: arXiv says '{title}'. Not adding it.")
    authors = [x.find("a:name", ns).text for x in ent.findall("a:author", ns)]
    year = ent.find("a:published", ns).text[:4]
    abstract = " ".join(ent.find("a:summary", ns).text.split())
    bib = (f"@misc{{x,\n  title={{{title}}},\n  author={{{' and '.join(authors)}}},\n  year={{{year}}},\n"
           f"  eprint={{{aid}}},\n  archivePrefix={{arXiv}}\n}}")
    meta = {"arxiv": aid, "title": title, "authors": authors, "year": int(year), "venue": "arXiv",
            "verified_via": "arxiv", "abstract": abstract}
    p = new_card(root, a.key or make_key(authors, year, title), meta, bib)
    print(f"candidate card: {p.relative_to(root)}\n  {title} ({year})")
    return p


def cmd_find(a):
    q = urllib.parse.urlencode({"query": a.query, "limit": a.n,
                                "fields": "title,year,authors,venue,externalIds,citationCount,isOpenAccess,abstract"})
    try:
        data = json.loads(http_get(f"https://api.semanticscholar.org/graph/v1/paper/search?{q}"))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"Semantic Scholar search failed ({e}). Fall back to web search, then add-doi to verify.")
    for i, p in enumerate(data.get("data", []), 1):
        ids = p.get("externalIds") or {}
        ident = f"doi:{ids['DOI']}" if ids.get("DOI") else f"arxiv:{ids['ArXiv']}" if ids.get("ArXiv") else "no-id"
        auth = (p.get("authors") or [{}])[0].get("name", "?")
        ab = " ".join((p.get("abstract") or "").split())[:260]
        print(f"{i}. {p.get('title')} ({p.get('year')}), {auth} et al., {p.get('venue') or '?'}; "
              f"cites={p.get('citationCount')} oa={p.get('isOpenAccess')} {ident}\n   {ab}")


DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>{}|\\^`]+)", re.I)
ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})(?:v\d+)?", re.I)


def ids_from_pdf(pdf: Path) -> tuple[str | None, str | None, str]:
    """Return (doi, arxiv_id, first_line) read from the first 3 pages of a PDF."""
    try:
        txt = subprocess.run(["pdftotext", "-l", "3", "-layout", str(pdf), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    except FileNotFoundError:
        sys.exit("pdftotext not installed (poppler-utils / `brew install poppler`)")
    flat = re.sub(r"-\s*\n\s*", "", txt)
    dois = [d.rstrip(".,;:)]'") for d in DOI_RE.findall(flat)]
    doi = max(set(dois), key=dois.count) if dois else None   # the DOI repeated most is the paper's own
    ax = ARXIV_RE.search(flat)
    first = next((l.strip() for l in txt.splitlines() if len(l.strip()) > 15), "")
    return doi, (ax.group(1) if ax else None), first


def expand_pdfs(items: list[str]) -> list[Path]:
    """PowerShell/cmd don't expand wildcards, so accept globs and folders here."""
    import glob
    out: list[Path] = []
    for it in items:
        pth = Path(it)
        if pth.is_dir():
            out += sorted(pth.glob("*.pdf"))
        elif any(c in it for c in "*?["):
            out += [Path(g) for g in sorted(glob.glob(it))]
        else:
            out.append(pth)
    return out


def cmd_add_pdf(a):
    """For each PDF: read its DOI/arXiv id, verify metadata online, create the inbox card, ingest the text."""
    root = find_root()
    rc = 0
    pdfs = expand_pdfs(a.pdfs)
    if not pdfs:
        sys.exit("no PDFs matched")
    for pdf in pdfs:
        print(f"== {pdf.name}")
        doi, ax, first = ids_from_pdf(pdf)
        if not doi and not ax:
            print(f"   no DOI or arXiv id found in the first pages (starts: '{first[:80]}'). Ask a human for the DOI, then run add-doi.")
            rc = 1
            continue
        try:
            if doi:
                p = cmd_add_doi(argparse.Namespace(doi=doi, key=a.key if len(pdfs) == 1 else None, expect_title=None))
            else:
                p = cmd_add_arxiv(argparse.Namespace(id=ax, key=a.key if len(pdfs) == 1 else None, expect_title=None))
        except SystemExit as e:
            print(f"   not added: {e}")
            rc = 1
            continue
        cmd_ingest(argparse.Namespace(pdf=str(pdf), key=p.stem))
    sys.exit(rc)


def cmd_ingest(a):
    root = find_root()
    pdf = Path(a.pdf)
    if not pdf.exists():
        sys.exit(f"{pdf} not found")
    try:
        raw = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    except FileNotFoundError:
        sys.exit("pdftotext not installed (poppler-utils / `brew install poppler`)")
    pages = raw.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    out = root / "refs" / "text" / f"{a.key}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(f"=== page {i} ===\n{p}\n" for i, p in enumerate(pages, 1)))
    dest = root / "refs" / "pdfs" / f"{a.key}.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if pdf.resolve() != dest.resolve():
        shutil.copy2(pdf, dest)
    words = len(raw.split())
    print(f"ingested {a.key}: {len(pages)} pages, {words} words -> refs/text/{a.key}.txt")
    for sub in ("cards", "inbox"):
        cp = root / "refs" / sub / f"{a.key}.md"
        if cp.exists():
            c = read_card(cp); c["access"] = "fulltext"; write_card(cp, c)
            print(f"card {sub}/{a.key}.md marked access: fulltext")
            break
    else:
        print("no card yet: run add-doi/add-arxiv with --key", a.key, "to get verified metadata")
    if words < 200 * max(1, len(pages)) // 4:
        print("WARN: very little text extracted; the PDF may be scanned. Quotes cannot be verified until it is OCR'd.")


def cmd_cards(a):
    root = find_root()
    bad = 0
    for k, c in all_cards(root).items():
        cl = c.get("claims") or []
        line = f"{c.get('status','?'):9} {k:24} {c.get('access','?'):13} claims={len(cl):<2} {str(c.get('title',''))[:60]}"
        if a.verify:
            fails = [str(x.get("id")) for x in cl if not quote_found(root, c, str(x.get("quote", "")))]
            if fails:
                bad += c.get("status") == "approved"
                line += f"  QUOTE-NOT-FOUND: {','.join(fails)}"
            if c.get("access") == "abstract-only" and any(x.get("strength") == "direct" for x in cl):
                line += "  (abstract-only card claims 'direct' support)"
        if not a.status or c.get("status") == a.status:
            print(line)
    if a.verify:
        print(f"--- {bad} approved card(s) with unverifiable quotes")
        sys.exit(1 if bad else 0)


def cmd_approve(a):
    root = find_root()
    src = root / "refs" / "inbox" / f"{a.key}.md"
    if not src.exists():
        sys.exit(f"refs/inbox/{a.key}.md not found")
    c = read_card(src)
    if not c.get("verified_via"):
        sys.exit("card has no verified_via; run add-doi/add-arxiv")
    fails = [str(x.get("id")) for x in c.get("claims") or [] if not quote_found(root, c, str(x.get("quote", "")))]
    if fails:
        sys.exit(f"claims {fails} have quotes not found in the text/abstract; fix before approving")
    c["status"] = "approved"
    c["approved_by"] = a.by or "user"
    c["approved_on"] = str(date.today())
    write_card(root / "refs" / "cards" / f"{a.key}.md", c)
    src.unlink()
    print(f"approved {a.key}; run `bib` to regenerate refs/library.bib")


def cmd_reject(a):
    root = find_root()
    for sub in ("inbox", "cards"):
        src = root / "refs" / sub / f"{a.key}.md"
        if src.exists():
            c = read_card(src); c["status"] = "rejected"; c["reject_reason"] = a.reason
            write_card(root / "refs" / "rejected" / f"{a.key}.md", c); src.unlink()
            print(f"rejected {a.key} (kept in refs/rejected/ so it is not re-proposed)")
            return
    sys.exit(f"{a.key} not in inbox or cards")


def cmd_bib(a):
    root = find_root()
    entries = [str(c["bibtex"]).strip() for c in all_cards(root).values() if c.get("status") == "approved" and c.get("bibtex")]
    out = root / "refs" / "library.bib"
    out.write_text("% GENERATED by paper.py bib from refs/cards (approved only). Do not edit by hand.\n\n"
                   + "\n\n".join(entries) + "\n")
    print(f"refs/library.bib: {len(entries)} entries")

# --------------------------------------------------------------------------- style + status

def word_diff(a: str, b: str) -> str:
    aw, bw = a.split(), b.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw).get_opcodes():
        if op == "equal":
            seg = aw[i1:i2]
            out.append(" ".join(seg) if len(seg) <= 8 else " ".join(seg[:3]) + " … " + " ".join(seg[-3:]))
        else:
            if i2 > i1:
                out.append("[-" + " ".join(aw[i1:i2]) + "-]")
            if j2 > j1:
                out.append("{+" + " ".join(bw[j1:j2]) + "+}")
    return " ".join(out)


def strip_comments(s: str) -> str:
    return "\n".join(split_line(l)[0] for l in s.splitlines() if not ANCHOR.match(l))


def cmd_style_diff(a):
    root = find_root(); cfg = load_cfg(root)
    snaps = {p.stem: p for p in (root / ".paper" / "drafts").glob("*.tex")}
    if not snaps:
        print("no draft snapshots yet")
        return
    current = {}
    for f in tex_files(root, cfg):
        for pid, flags, ln, body in paragraphs(f):
            current[pid] = (flags, "\n".join(body))
    changed = 0
    for pid, sp in sorted(snaps.items()):
        if pid not in current:
            print(f"## {pid}: deleted by humans")
            continue
        flags, now = current[pid]
        before, after = strip_comments(sp.read_text()), strip_comments(now)
        if norm(before) == norm(after):
            continue
        changed += 1
        print(f"## {pid}{' (still marked draft)' if 'draft' in flags else ''}\n{word_diff(before, after)}\n")
        if a.accept:
            sp.write_text(now + "\n")
    print(f"--- {changed} paragraph(s) edited by humans since Claude drafted them"
          + ("; snapshots updated" if a.accept and changed else ""))


def cmd_status(a):
    root = find_root(); cfg = load_cfg(root)
    st = root / "STATE.md"
    if st.exists():
        print(st.read_text().strip())
    cards = all_cards(root)
    cnt = {}
    for c in cards.values():
        cnt[c.get("status", "?")] = cnt.get(c.get("status", "?"), 0) + 1
    drafts = [pid for f in tex_files(root, cfg) for pid, fl, *_ in paragraphs(f) if "draft" in fl]
    reg = registry(cfg)
    code = cfg["code_repo_path"]
    head = "?"
    try:
        head = subprocess.run(["git", "-C", str(code), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip() or "?"
    except FileNotFoundError:
        pass
    last = (root / ".paper" / "code_head").read_text().strip() if (root / ".paper" / "code_head").exists() else None
    print(f"\n--- library: {cnt}; drafts awaiting human edit: {len(drafts)} {drafts[:8]}")
    print(f"--- code repo {code.name} @ {head}; registry: {len(reg)} experiments "
          f"({', '.join(str(k) + '=' + str(v.get('status')) for k, v in list(reg.items())[:20])})")
    if last and last != head and head != "?":
        diff = subprocess.run(["git", "-C", str(code), "diff", "--name-only", last, "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.split()
        touched = [p for p in diff if p.startswith(("results/", "experiments/", "configs/"))]
        print(f"--- code changed since last session ({last}..{head}); evidence-relevant files: {touched[:12] or 'none'}"
              "\n    re-run `check` so STALE numbers surface")
    if head != "?":
        (root / ".paper" / "code_head").write_text(head + "\n")

# --------------------------------------------------------------------------- init

def cmd_init(a):
    dest = Path(a.dir).resolve()
    tmpl = HERE.parent / "assets" / "paper_template"
    if dest.exists() and any(dest.iterdir()) and not a.force:
        sys.exit(f"{dest} is not empty (use --force to add missing files only)")
    for src in tmpl.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(tmpl)
        out = dest / str(rel).replace("dot_", ".")
        if out.exists():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        txt = src.read_text()
        txt = txt.replace("{{TITLE}}", a.title).replace("{{CODE_REPO}}", a.code_repo).replace(
            "{{CODE_REPO_NAME}}", Path(a.code_repo).name).replace("{{CODE_GH}}", a.code_github or "OWNER/REPO")
        out.write_text(txt)
    for d in ("refs/cards", "refs/inbox", "refs/rejected", "refs/text", "refs/pdfs", ".paper/drafts"):
        (dest / d).mkdir(parents=True, exist_ok=True)
        keep = dest / d / ".gitkeep"
        if not any((dest / d).iterdir()):
            keep.touch()
    tools = dest / "tools"
    tools.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), tools / "paper.py")
    print(f"scaffolded {dest}\n  code repo: {a.code_repo}\n  next: git init, fill outline.md with the team, "
          "then `python tools/paper.py status`")

# --------------------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="paper.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("status").set_defaults(fn=cmd_status)
    x = s.add_parser("para"); x.add_argument("id"); x.add_argument("--snapshot", action="store_true"); x.set_defaults(fn=cmd_para)
    x = s.add_parser("evidence"); x.add_argument("ref"); x.set_defaults(fn=cmd_evidence)
    x = s.add_parser("search"); x.add_argument("query"); x.add_argument("-k", type=int, default=6); x.set_defaults(fn=cmd_search)
    x = s.add_parser("page"); x.add_argument("key"); x.add_argument("n", type=int)
    x.add_argument("--grep"); x.add_argument("--max-chars", type=int, default=3500); x.set_defaults(fn=cmd_page)
    x = s.add_parser("find"); x.add_argument("query"); x.add_argument("-n", type=int, default=8); x.set_defaults(fn=cmd_find)
    x = s.add_parser("add-doi"); x.add_argument("doi"); x.add_argument("--key"); x.add_argument("--expect-title"); x.set_defaults(fn=cmd_add_doi)
    x = s.add_parser("add-arxiv"); x.add_argument("id"); x.add_argument("--key"); x.add_argument("--expect-title"); x.set_defaults(fn=cmd_add_arxiv)
    x = s.add_parser("add-pdf"); x.add_argument("pdfs", nargs="+"); x.add_argument("--key"); x.set_defaults(fn=cmd_add_pdf)
    x = s.add_parser("ingest"); x.add_argument("pdf"); x.add_argument("--key", required=True); x.set_defaults(fn=cmd_ingest)
    x = s.add_parser("cards"); x.add_argument("--verify", action="store_true"); x.add_argument("--status"); x.set_defaults(fn=cmd_cards)
    x = s.add_parser("approve"); x.add_argument("key"); x.add_argument("--by"); x.set_defaults(fn=cmd_approve)
    x = s.add_parser("reject"); x.add_argument("key"); x.add_argument("--reason", required=True); x.set_defaults(fn=cmd_reject)
    s.add_parser("bib").set_defaults(fn=cmd_bib)
    x = s.add_parser("check"); x.add_argument("files", nargs="*"); x.add_argument("--errors-only", action="store_true")
    x.add_argument("--lenient", action="store_true", help="skip NO-PROVENANCE warnings"); x.set_defaults(fn=cmd_check)
    x = s.add_parser("style-diff"); x.add_argument("--accept", action="store_true"); x.set_defaults(fn=cmd_style_diff)
    x = s.add_parser("init"); x.add_argument("dir"); x.add_argument("--code-repo", required=True)
    x.add_argument("--code-github"); x.add_argument("--title", default="Working paper")
    x.add_argument("--force", action="store_true"); x.set_defaults(fn=cmd_init)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
