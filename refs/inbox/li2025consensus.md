---
key: li2025consensus
doi: 10.3390/math13162570
title: Consensus-Regularized Federated Learning for Superior Generalization in Wind Turbine Diagnostics
authors:
- Lan Li
- Juncheng Zhou
- Qiankun Peng
- Quan Zhou
- Haoming Zhang
year: 2025
venue: Mathematics
verified_via: crossref
abstract: Ensuring the reliable operation of wind turbines is critical for the global transition to sustainable
  energy, yet it is challenged by faults that are difficult to detect in real-time. Traditional diagnostics
  rely on centralized data, which raises significant privacy and scalability concerns. To address these
  limitations, this study introduces a Consensus-Regularized Federated Learning (CR-FL) framework. This
  framework mathematically formalizes and mitigates the problem of “client drift” caused by heterogeneous
  data from different turbines by augmenting the local training objective with a proximal regularization
  term. This forces models to learn generalizable fault features while preserving data privacy. To validate
  our framework, we implemented a lightweight neural network within a federated paradigm and benchmarked
  it against a powerful, centralized Light Gradient Boosting Machine (LightGBM) model using real-world
  SCADA data. The federated training process, through its inherent constraint on local updates, acts as
  a practical implementation of our consensus-regularization principle. Model performance was comprehensively
  evaluated using accuracy, precision, F1-score, and Area Under the ROC Curve (AUC) metrics. The results
  demonstrate that our federated approach not only preserves privacy but also achieves superior performance
  in key metrics, including AUC and precision. This confirms that the regularizing effect of the federated
  process enables the global model to generalize better across heterogeneous data distributions than its
  centralized counterpart. This study provides a practical, scalable, and methodologically superior solution
  for fault diagnosis in wind turbine systems, paving the way for more collaborative and secure infrastructure
  monitoring.
verified_on: '2026-10-27'
status: candidate
access: fulltext
relevance: "[context] Proximal-regularised FL for wind turbine diagnostics is the nearest wind use of the FedProx idea, but it targets supervised diagnosis, not NBM."
claims: []
bibtex: '@article{li2025consensus, title={Consensus-Regularized Federated Learning for Superior Generalization
  in Wind Turbine Diagnostics}, volume={13}, ISSN={2227-7390}, url={http://dx.doi.org/10.3390/math13162570},
  DOI={10.3390/math13162570}, number={16}, journal={Mathematics}, publisher={MDPI AG}, author={Li, Lan
  and Zhou, Juncheng and Peng, Qiankun and Zhou, Quan and Zhang, Haoming}, year={2025}, month=Aug, pages={2570}
  }

  '
---

Notes (human or Claude): why this paper matters for *our* paper.
