---
key: mcmahan2016communication
arxiv: '1602.05629'
title: Communication-Efficient Learning of Deep Networks from Decentralized Data
authors:
- H. Brendan McMahan
- Eider Moore
- Daniel Ramage
- Seth Hampson
- Blaise Agüera y Arcas
year: 2016
venue: arXiv
verified_via: arxiv
abstract: Modern mobile devices have access to a wealth of data suitable for learning models, which in
  turn can greatly improve the user experience on the device. For example, language models can improve
  speech recognition and text entry, and image models can automatically select good photos. However, this
  rich data is often privacy sensitive, large in quantity, or both, which may preclude logging to the
  data center and training there using conventional approaches. We advocate an alternative that leaves
  the training data distributed on the mobile devices, and learns a shared model by aggregating locally-computed
  updates. We term this decentralized approach Federated Learning. We present a practical method for the
  federated learning of deep networks based on iterative model averaging, and conduct an extensive empirical
  evaluation, considering five different model architectures and four datasets. These experiments demonstrate
  the approach is robust to the unbalanced and non-IID data distributions that are a defining characteristic
  of this setting. Communication costs are the principal constraint, and we show a reduction in required
  communication rounds by 10-100x as compared to synchronized stochastic gradient descent.
verified_on: '2026-10-27'
status: approved
access: fulltext
relevance: '[core] FedAvg is the aggregation rule behind our F1 arm and the base that F2-F4 modify.'
claims:
- id: c1
  text: Federated learning keeps training data on the clients and learns a shared model from aggregated
    local updates.
  quote: We advocate an alternative that leaves the training data distributed on the mobile devices, and
    learns a shared model by aggregating locally-computed updates.
  loc: Abstract, p.1
  strength: direct
- id: c2
  text: FedSGD is one local gradient step per client followed by a weighted average of the client models.
  quote: each client locally takes one step of gradient descent on the current model using its local data,
    and the server then takes a weighted average of the resulting models.
  loc: §2, p.4
  strength: direct
- id: c3
  text: FedAvg is controlled by the client fraction C, the number of local epochs E and the local minibatch
    size B.
  quote: C, the fraction of clients that perform computation on each round; E, then number of training
    passes each client makes over its local dataset on each round; and B, the local minibatch size
  loc: §2, p.4
  strength: direct
- id: c4
  text: The authors report FedAvg is robust to unbalanced and non-IID client data.
  quote: These experiments demonstrate the approach is robust to the unbalanced and non-IID data distributions
    that are a defining characteristic of this setting.
  loc: Abstract, p.1
  numbers: evidence is MNIST, CIFAR-10 and Shakespeare language modelling, not sensor time series
  strength: direct
- id: c5
  text: On the pathologically non-IID MNIST split FedAvg's round savings shrink but stay substantial.
  quote: The speedups for the pathologically partitioned non-IID data are smaller, but still substantial
  loc: §3, p.6
  numbers: 'MNIST non-IID (2 digits per client, 100 clients): 2.8-3.7x fewer rounds; IID: 35x (CNN), 46x
    (2NN)'
  strength: direct
- id: c6
  text: Averaging models that start from a shared initialisation works well, which is why every FedAvg
    round starts from the same global model.
  quote: when we start two models from the same random initialization and then again train each independently
    on a different subset of the data (as described above), we find that naive parameter averaging works
    surprisingly well
  loc: §2, p.4
  strength: direct
- id: c7
  text: Formal privacy guarantees (differential privacy, secure computation) are left as future work.
  quote: While federated learning offers many practical privacy benefits, providing stronger guarantees
    via differential privacy ... secure multi-party computation ... or their combination is an interesting
    direction for future work.
  loc: §4, p.8
  strength: background
bibtex: "@misc{mcmahan2016communication,\n  title={Communication-Efficient Learning of Deep Networks from\
  \ Decentralized Data},\n  author={H. Brendan McMahan and Eider Moore and Daniel Ramage and Seth Hampson\
  \ and Blaise Agüera y Arcas},\n  year={2016},\n  eprint={1602.05629},\n  archivePrefix={arXiv}\n}\n"
approved_by: user
approved_on: '2026-10-27'
---

Notes (human or Claude): why this paper matters for *our* paper.
