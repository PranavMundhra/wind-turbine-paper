---
key: karimireddy2020scaffold
arxiv: '1910.06378'
title: 'SCAFFOLD: Stochastic Controlled Averaging for Federated Learning'
authors:
- Sai Praneeth Karimireddy
- Satyen Kale
- Mehryar Mohri
- Sashank J. Reddi
- Sebastian U. Stich
- Ananda Theertha Suresh
year: 2019
venue: arXiv
verified_via: arxiv
abstract: Federated Averaging (FedAvg) has emerged as the algorithm of choice for federated learning due
  to its simplicity and low communication cost. However, in spite of recent research efforts, its performance
  is not fully understood. We obtain tight convergence rates for FedAvg and prove that it suffers from
  `client-drift' when the data is heterogeneous (non-iid), resulting in unstable and slow convergence.
  As a solution, we propose a new algorithm (SCAFFOLD) which uses control variates (variance reduction)
  to correct for the `client-drift' in its local updates. We prove that SCAFFOLD requires significantly
  fewer communication rounds and is not affected by data heterogeneity or client sampling. Further, we
  show that (for quadratics) SCAFFOLD can take advantage of similarity in the client's data yielding even
  faster convergence. The latter is the first result to quantify the usefulness of local-steps in distributed
  optimization.
verified_on: '2026-10-27'
status: approved
access: fulltext
relevance: '[core] SCAFFOLD corrects client drift with control variates, a heterogeneity-aware comparator
  for F1-F3 that the registry does not yet include.'
claims:
- id: c1
  text: SCAFFOLD is proved to need fewer communication rounds than FedAvg and to be unaffected by data
    heterogeneity and client sampling.
  quote: We prove that SCAFFOLD requires significantly fewer communication rounds and is not affected
    by data heterogeneity or client sampling.
  loc: Abstract, p.1
  strength: direct
- id: c2
  text: The paper's analysis finds FedAvg can be hurt by gradient dissimilarity across clients and be
    slower than plain SGD.
  quote: Our careful theoretical analysis showed that FEDAVG can be severely hampered by gradient dissimilarity,
    and can be even slower than SGD.
  loc: §8, p.8
  strength: direct
- id: c3
  text: SCAFFOLD keeps a control variate on the server and on every client, so clients are stateful.
  quote: Along with the server model x, SCAFFOLD maintains a state for each client (client control variate
    ci) and for the server (server control variate c).
  loc: §4, p.4
  strength: direct
- id: c4
  text: In the authors' experiments SCAFFOLD beat SGD and FedAvg in every setting tried.
  quote: SCAFFOLD consistently outperforms SGD and FEDAVG across all parameter regimes
  loc: §7, p.7
  numbers: simulated quadratics and EMNIST (100 clients); not sensor data
  strength: direct
- id: c5
  text: In their EMNIST runs FedProx was always slower than the other local-update methods.
  quote: The latter FEDPROX is always slower than the other local update methods, though in some cases
    it outperforms SGD.
  loc: §7.3, p.7
  strength: direct
- id: c6
  text: They fixed FedProx's regularisation for the comparison and note that tuning it might improve FedProx.
  quote: Additional tuning of the regularization parameter may sometimes yield improved empirical performance.
  loc: §7.1, p.7
  numbers: FedProx regularisation fixed at 1
  strength: direct
- id: c7
  text: With fully heterogeneous clients FedAvg slows as local steps increase and falls behind SGD after
    5 epochs.
  quote: When similarity is 0%, FEDAVG gets slower with increasing local steps. If we take more than 5
    epochs, its performance is worse than SGD's.
  loc: §7.3, p.7
  numbers: EMNIST logistic regression, 0% client similarity, threshold 0.5 test accuracy
  strength: direct
- id: c8
  text: On a small non-convex EMNIST network SCAFFOLD ended with higher accuracy than FedAvg, which the
    authors call preliminary.
  quote: We see that SCAFFOLD is better than FEDAVG in terms of final test accuracy reached, though interestingly
    FEDAVG seems better than SGD even when similarity is 0.
  loc: §7.3, p.8
  numbers: 'EMNIST 2-layer net, 1k rounds, 5 epochs, 20% clients per round, 0% similarity: SGD 0.766,
    FedAvg 0.787, SCAFFOLD 0.801'
  strength: direct
bibtex: "@misc{karimireddy2020scaffold,\n  title={SCAFFOLD: Stochastic Controlled Averaging for Federated\
  \ Learning},\n  author={Sai Praneeth Karimireddy and Satyen Kale and Mehryar Mohri and Sashank J. Reddi\
  \ and Sebastian U. Stich and Ananda Theertha Suresh},\n  year={2019},\n  eprint={1910.06378},\n  archivePrefix={arXiv}\n\
  }\n"
approved_by: user
approved_on: '2026-10-27'
---

Notes (human or Claude): why this paper matters for *our* paper.
