---
key: li2018federated
arxiv: '1812.06127'
title: Federated Optimization in Heterogeneous Networks
authors:
- Tian Li
- Anit Kumar Sahu
- Manzil Zaheer
- Maziar Sanjabi
- Ameet Talwalkar
- Virginia Smith
year: 2018
venue: arXiv
verified_via: arxiv
abstract: 'Federated Learning is a distributed learning paradigm with two key challenges that differentiate
  it from traditional distributed optimization: (1) significant variability in terms of the systems characteristics
  on each device in the network (systems heterogeneity), and (2) non-identically distributed data across
  the network (statistical heterogeneity). In this work, we introduce a framework, FedProx, to tackle
  heterogeneity in federated networks. FedProx can be viewed as a generalization and re-parametrization
  of FedAvg, the current state-of-the-art method for federated learning. While this re-parameterization
  makes only minor modifications to the method itself, these modifications have important ramifications
  both in theory and in practice. Theoretically, we provide convergence guarantees for our framework when
  learning over data from non-identical distributions (statistical heterogeneity), and while adhering
  to device-level systems constraints by allowing each participating device to perform a variable amount
  of work (systems heterogeneity). Practically, we demonstrate that FedProx allows for more robust convergence
  than FedAvg across a suite of realistic federated datasets. In particular, in highly heterogeneous settings,
  FedProx demonstrates significantly more stable and accurate convergence behavior relative to FedAvg---improving
  absolute test accuracy by 22% on average.'
verified_on: '2026-10-27'
status: approved
access: fulltext
relevance: '[core] FedProx''s proximal term is exactly what the F3 mu sweep varies, so we build on it
  and cite it for the method.'
claims:
- id: c1
  text: FedProx generalises FedAvg; the proximal term is the added piece.
  quote: FedProx can be viewed as a generalization and re-parametrization of FedAvg, the current state-of-the-art
    method for federated learning.
  loc: Abstract, p.1
  strength: direct
- id: c2
  text: The proximal term keeps local updates near the global model without hand-setting the number of
    local epochs.
  quote: It addresses the issue of statistical heterogeneity by restricting the local updates to be closer
    to the initial (global) model without any need to manually set the number of local epochs.
  loc: §3.2, p.4
  strength: direct
- id: c3
  text: Many local epochs on heterogeneous data can push local models away from the global model and cause
    divergence.
  quote: Intuitively, large E may cause local models to drift too far away from the initial starting point,
    thus leading to potential divergence
  loc: §5.3.2, p.9
  strength: direct
- id: c4
  text: The proximal term can slow convergence when the data are IID.
  quote: Though it may slow convergence for IID data
  loc: §5.3.1, p.9
  strength: direct
- id: c5
  text: On their realistic federated datasets FedProx improved absolute test accuracy over FedAvg by 22%
    on average in the most heterogeneous setting.
  quote: FedProx improves absolute testing accuracy relative to FedAvg by 22% on average in highly heterogeneous
    environments (90% stragglers)
  loc: §5.3.2, p.9
  numbers: 22% absolute test-accuracy gain, mean over datasets, 90% stragglers; supervised classification/LM
    tasks
  strength: direct
- id: c6
  text: The authors tuned the proximal weight over a four-value grid.
  quote: from the limited candidate set {0.001, 0.01, 0.1, 1}
  loc: §5.3.2, p.10
  numbers: 'mu grid {0.001, 0.01, 0.1, 1}; best mu on the five federated datasets: 1, 1, 1, 0.001, 0.01'
  strength: direct
- id: c7
  text: They prove convergence for FedProx on non-identically distributed client data.
  quote: we provide convergence guarantees for our framework when learning over data from non-identical
    distributions (statistical heterogeneity)
  loc: Abstract, p.1
  strength: direct
- id: c8
  text: Differential privacy and secure multiparty computation can be combined with FedProx.
  quote: standard privacy-preserving approaches such as differential privacy and secure multiparty communication
    can naturally be combined with the methods proposed herein
  loc: §1, footnote 1, p.1
  strength: background
bibtex: "@misc{li2018federated,\n  title={Federated Optimization in Heterogeneous Networks},\n  author={Tian\
  \ Li and Anit Kumar Sahu and Manzil Zaheer and Maziar Sanjabi and Ameet Talwalkar and Virginia Smith},\n\
  \  year={2018},\n  eprint={1812.06127},\n  archivePrefix={arXiv}\n}\n"
approved_by: user
approved_on: '2026-10-27'
---

Notes (human or Claude): why this paper matters for *our* paper.
