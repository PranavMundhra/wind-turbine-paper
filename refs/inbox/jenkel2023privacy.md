---
key: jenkel2023privacy
doi: 10.3390/en16176377
title: Privacy-Preserving Fleet-Wide Learning of Wind Turbine Conditions with Federated Learning
authors:
- Lorin Jenkel
- Stefan Jonas
- Angela Meyer
year: 2023
venue: Energies
verified_via: crossref
abstract: A wealth of data is constantly being collected by manufacturers from their wind turbine fleets.
  And yet, a lack of data access and sharing impedes exploiting the full potential of the data. Our study
  presents a privacy-preserving machine learning approach for fleet-wide learning of condition information
  without sharing any data locally stored on the wind turbines. We show that through federated fleet-wide
  learning, turbines with little or no representative training data can benefit from accuracy gains from
  improved normal behavior models. Customizing the global federated model to individual turbines yields
  the highest fault detection accuracy in cases where the monitored target variable is distributed heterogeneously
  across the fleet. We demonstrate this for bearing temperatures, a target variable whose normal behavior
  can vary widely depending on the turbine. We show that no member of the fleet is affected by a degradation
  in model accuracy by participating in the collaborative learning procedure, resulting in superior performance
  of the federated learning strategy in our case studies. Distributed learning increases the normal behavior
  model training times by about a factor of ten due to increased communication overhead and slower model
  convergence.
verified_on: '2026-10-27'
status: candidate
access: fulltext
relevance: "[core] Fleet-wide federated NBMs with per-turbine customisation of the global model are the nearest comparison for our F2 versus local D."
claims: []
bibtex: '@article{jenkel2023privacy, title={Privacy-Preserving Fleet-Wide Learning of Wind Turbine Conditions
  with Federated Learning}, volume={16}, ISSN={1996-1073}, url={http://dx.doi.org/10.3390/en16176377},
  DOI={10.3390/en16176377}, number={17}, journal={Energies}, publisher={MDPI AG}, author={Jenkel, Lorin
  and Jonas, Stefan and Meyer, Angela}, year={2023}, month=Sept, pages={6377} }

  '
---

Notes (human or Claude): why this paper matters for *our* paper.
