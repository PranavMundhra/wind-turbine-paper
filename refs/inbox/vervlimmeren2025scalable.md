---
key: vervlimmeren2025scalable
doi: 10.5194/wes-10-2615-2025
title: Scalable SCADA-driven failure prediction for offshore wind turbines using autoencoder-based NBM
  and fleet-median filtering
authors:
- Ivo Vervlimmeren
- Xavier Chesterman
- Timothy Verstraeten
- Ann Nowé
- Jan Helsen
year: 2025
venue: Wind Energy Science
verified_via: crossref
abstract: 'Offshore wind turbines are crucial for sustainable energy production but face significant challenges
  in operational reliability and maintenance costs. In particular, the scalability and practicality of
  failure detection systems are a key challenge in large-scale wind farms. This paper presents a scalable,
  comprehensive approach to failure prediction based on the normal behavior modeling (NBM) framework that
  integrates three components: a cloud-based pipeline, an undercomplete autoencoder for temperature-based
  anomaly detection, and a time-aware anomaly filtering method. The pipeline enables dynamic scaling and
  streamlined deployment across multiple wind farms. The autoencoder was trained exclusively on healthy
  10 min SCADA data and produces detailed anomaly scores that serve as the input for our filtering technique.
  It was trained on 4 years of data from a large offshore wind farm in the Dutch–Belgian zone and achieved
  unhealthy–healthy (UHH) ratios of up to 1.69 and 1.21 for the generator and gearbox models, respectively.
  The filtering method refines the raw anomaly scores by comparing turbine signals to a windowed fleet
  median. By aggregating scores via sliding windows and employing robust distance metrics, the method
  reduces the volume of anomaly scores by up to 65 % without sacrificing predictive accuracy. This selective
  filtering effectively minimizes noise and non-relevant anomalies, enhancing the efficiency of maintenance
  analysis.'
verified_on: '2026-10-27'
status: candidate
access: fulltext
relevance: "[core] Autoencoder NBM on multi-turbine SCADA with fleet-level filtering matches our model class and fleet setting."
claims: []
bibtex: '@article{vervlimmeren2025scalable, title={Scalable SCADA-driven failure prediction for offshore
  wind turbines using autoencoder-based NBM and fleet-median filtering}, volume={10}, ISSN={2366-7451},
  url={http://dx.doi.org/10.5194/wes-10-2615-2025}, DOI={10.5194/wes-10-2615-2025}, number={11}, journal={Wind
  Energy Science}, publisher={Copernicus GmbH}, author={Vervlimmeren, Ivo and Chesterman, Xavier and Verstraeten,
  Timothy and Nowé, Ann and Helsen, Jan}, year={2025}, month=Nov, pages={2615–2637} }

  '
---

Notes (human or Claude): why this paper matters for *our* paper.
