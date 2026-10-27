---
key: gueck2024care
doi: 10.3390/data9120138
title: 'CARE to Compare: A Real-World Benchmark Dataset for Early Fault Detection in Wind Turbine Data'
authors:
- Christian Gück
- Cyriana M. A. Roelofs
- Stefan Faulstich
year: 2024
venue: Data
verified_via: crossref
abstract: Early fault detection plays a crucial role in the field of predictive maintenance for wind turbines,
  yet the comparison of different algorithms poses a difficult task because domain-specific public datasets
  are scarce. Many comparisons of different approaches either use benchmarks composed of data from many
  different domains, inaccessible data, or one of the few publicly available datasets that lack detailed
  information about the faults. Moreover, many publications highlight a couple of case studies where fault
  detection was successful. With this paper, we publish a high quality dataset that contains data from
  36 wind turbines across 3 different wind farms as well as the most detailed fault information of any
  public wind turbine dataset as far as we know. The new dataset contains 89 years worth of real-world
  operating data of wind turbines, distributed across 44 labeled time frames for anomalies that led up
  to faults, as well as 51 time series representing normal behavior. Additionally, the quality of training
  data is ensured by turbine-status-based labels for each data point. Furthermore, we propose a new scoring
  method, called CARE (Coverage, Accuracy, Reliability and Earliness), which takes advantage of the information
  depth that is present in the dataset to identify good early fault detection models for wind turbines.
  This score considers the anomaly detection performance, the ability to recognize normal behavior properly,
  and the capability to raise as few false alarms as possible while simultaneously detecting anomalies
  early.
verified_on: '2026-10-27'
status: approved
access: fulltext
relevance: '[core] Defines the CARE benchmark dataset and score that every one of our arms is evaluated
  with, so it anchors the Data and Results sections.'
claims:
- id: c1
  text: The CARE benchmark holds 95 SCADA datasets from 36 turbines on three wind farms, about half with
    a labelled anomaly event.
  quote: The data consists of 95 datasets, containing 89 years of SCADA time series distributed across
    36 different WTs from the three wind farms A, B and C.
  loc: §3.2, p.8
  numbers: 95 datasets; 89 years; 36 turbines; 44 anomaly-event and 51 normal datasets (p.8)
  strength: direct
- id: c2
  text: Each dataset has 10-minute SCADA data, one training year and a short prediction window.
  quote: The datasets consist of SCADA time series data for each turbine, with a resolution of 10 minutes.
    Each dataset includes one year worth of data for training a model, as well as 4 to 98 days of prediction
    data.
  loc: §3.2, p.8
  numbers: 10-minute resolution; 1 year training; 4-98 days prediction
  strength: direct
- id: c3
  text: Farm C is the largest farm in CARE and has by far the most features.
  quote: Wind farm A has 86 features, wind farm B has 257 features, and wind farm C has 957 features.
  loc: §3.2, p.8 (counts per farm in the table on p.9)
  numbers: 'Farm C: 22 turbines, 58 datasets (27 anomaly events, 31 normal), 957 features, 238 sensors
    (table, p.9)'
  strength: direct
- id: c4
  text: 'CARE scores four aspects of an anomaly detector: coverage, accuracy, reliability and earliness.'
  quote: 'Coverage: Detection of as many correct anomalies as possible, 2. Accuracy: Recognition of normal
    behavior, 3. Reliability: Few false alarm events, 4. Earliness: Detection of anomalies before fault
    gets critical.'
  loc: §4.1, p.12
  strength: direct
- id: c5
  text: 'Reliability is scored per event: an event counts as detected only once a criticality counter
    reaches 72.'
  quote: in order to reach a criticality of 72 the algorithm must either detect at least 72 anomalies
    in a row, which equates to 12 hours of consecutive anomalies
  loc: §4.1.1 (Reliability), p.14
  numbers: threshold t_c = 72 steps = 12 h of 10-minute data
  strength: direct
- id: c6
  text: CARE is 0 if nothing is detected and falls back to the accuracy sub-score when that is below 0.5.
  quote: If no anomalies were detected at all, the CARE score will be 0. Also, if Acc falls below 0.5,
    the predictions are worse than uniformly distributed random predictions.
  loc: §4.1.1 (CARE), p.16
  numbers: CARE = 0 if no anomaly detected; CARE = Acc if Acc < 0.5
  strength: direct
- id: c7
  text: On the whole 95-dataset benchmark the authors' autoencoder normal-behaviour model scored CARE
    0.66.
  quote: With a score of 0.66 the AE approach represents a good anomaly detector since it is able to detect
    anomalies while also recognizing normal behavior very well
  loc: §4.2.3, p.20
  numbers: CARE 0.66 over all 95 datasets (all three farms); random baseline 0.5
  strength: direct
- id: c8
  text: For Farm C the benchmark autoencoder uses one fixed threshold calibrated on its validation reconstruction
    errors.
  quote: For wind farm C, a fixed threshold is calibrated. For this, the L2-norm of the reconstruction
    errors (anomaly score) of all AE validation data is computed.
  loc: §4.2.2, p.19
  strength: direct
bibtex: '@article{gueck2024care, title={CARE to Compare: A Real-World Benchmark Dataset for Early Fault
  Detection in Wind Turbine Data}, volume={9}, ISSN={2306-5729}, url={http://dx.doi.org/10.3390/data9120138},
  DOI={10.3390/data9120138}, number={12}, journal={Data}, publisher={MDPI AG}, author={Gück, Christian
  and Roelofs, Cyriana M. A. and Faulstich, Stefan}, year={2024}, month=Nov, pages={138} }

  '
approved_by: user
approved_on: '2026-10-27'
---

Notes (human or Claude): why this paper matters for *our* paper.
