---
key: roelofs2024transfer
arxiv: '2404.03011'
title: Transfer learning applications for anomaly detection in wind turbines
authors:
- Cyriana M. A. Roelofs
- Christian Gück
- Stefan Faulstich
year: 2024
venue: arXiv
verified_via: arxiv
abstract: 'Anomaly detection in wind turbines typically involves using normal behaviour models to detect
  faults early. However, training autoencoder models for each turbine is time-consuming and resource intensive.
  Thus, transfer learning becomes essential for wind turbines with limited data or applications with limited
  computational resources. This study examines how cross-turbine transfer learning can be applied to autoencoder-based
  anomaly detection. Here, autoencoders are combined with constant thresholds for the reconstruction error
  to determine if input data contains an anomaly. The models are initially trained on one year''s worth
  of data from one or more source wind turbines. They are then fine-tuned using smaller amounts of data
  from another turbine. Three methods for fine-tuning are investigated: adjusting the entire autoencoder,
  only the decoder, or only the threshold of the model. The performance of the transfer learning models
  is compared to baseline models that were trained on one year''s worth of data from the target wind turbine.
  The results of the tests conducted in this study indicate that models trained on data of multiple wind
  turbines do not improve the anomaly detection capability compared to models trained on data of one source
  wind turbine. In addition, modifying the model''s threshold can lead to comparable or even superior
  performance compared to the baseline, whereas fine-tuning the decoder or autoencoder further enhances
  the models'' performance.'
verified_on: '2026-10-27'
status: candidate
access: fulltext
relevance: "[core] Cross-turbine transfer for autoencoder NBMs is the non-federated alternative to compare against our local (D) and shared-encoder (F2) arms."
claims: []
bibtex: "@misc{roelofs2024transfer,\n  title={Transfer learning applications for anomaly detection in\
  \ wind turbines},\n  author={Cyriana M. A. Roelofs and Christian Gück and Stefan Faulstich},\n  year={2024},\n\
  \  eprint={2404.03011},\n  archivePrefix={arXiv}\n}\n"
---

Notes (human or Claude): why this paper matters for *our* paper.
