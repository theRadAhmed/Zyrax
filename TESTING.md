# ZyraX Testing

Backend tested with Flask's test client (version 2.1). The Open Targets call
was mocked for the scenario and validation tests, and tested separately with
simulated API responses. A live Open Targets check is done with
`python check_open_targets.py`.

## Test summary

37 scenario tests and 11 validation/API tests, all passing (see tables).
Run against the 15-condition knowledge base with Open Targets mocked.

## Prototype rules

| Parameter | Flagged abnormal when |
|---|---|
| Blood pressure | systolic > 130 or diastolic > 80 |
| Temperature | >= 100.4 °F (38 °C) |
| Fasting glucose (low) | < 70 mg/dL; borderline 100-125 |
| HbA1c (borderline) | 5.7-6.4 % |
| Hemoglobin (high) | > 17 g/dL |
| TSH (low) | < 0.4 mIU/L |
| Platelets | < 150 or > 450 ×10³/µL |
| WBC | < 4 or > 11 ×10³/µL |
| Blood pressure (low) | systolic < 90 or diastolic < 60 |
| Fasting glucose | >= 126 mg/dL |
| HbA1c | >= 6.5 % |
| Hemoglobin | < 12 g/dL |
| TSH | > 4.5 mIU/L |

## Scenario tests

| ID | Input | Abnormal | Associations (rule-match score) |
|---|---|---|---|
| T1 | BP 110/70, glucose 90, HbA1c 5.2, Hb 14, TSH 2.1, temp 36.8, plt 250, WBC 7 | 0 / 8 | none |
| T2 | BP 120/80, glucose 140, HbA1c 7.2, Hb 11, TSH 5.2, temp 37, plt 250, WBC 7.5 | 4 / 8 | Type 2 Diabetes 100, Iron-Deficiency Anemia 100, Hypothyroidism 100 |
| T3 | glucose 180, HbA1c 8.5 | 2 / 2 | Type 2 Diabetes 100 |
| T4 | Hb 8.5 | 1 / 1 | Iron-Deficiency Anemia 100 |
| T5 | TSH 9.0 | 1 / 1 | Hypothyroidism 100 |
| T6 | BP 160/100 | 1 / 1 | Hypertension 100 |
| T7 | glucose 130 | 1 / 1 | Type 2 Diabetes 44.4 |
| T8 | HbA1c 6.8 | 1 / 1 | Type 2 Diabetes 55.6 |
| T9 | glucose 126 (boundary) | 1 / 1 | Type 2 Diabetes 44.4 |
| T10 | Hb 12 (boundary) | 0 / 1 | none |
| T11 | temp 103.1 °F, WBC 15 | 2 / 2 | Bacterial Infection 100, Dengue 42.9 |
| T12 | platelets 60 | 1 / 1 | Thrombocytopenia 100, Dengue 57.1 |
| T13 | BP 150/95, glucose 200, HbA1c 9, Hb 9, TSH 8 | 5 / 5 | Type 2 Diabetes 100, Hypertension 100, Iron-Deficiency Anemia 100, Hypothyroidism 100 |

## Validation and error tests

| ID | Input | Expected | Result |
|---|---|---|---|
| V1 | `{}` | HTTP 400 | Pass |
| V2 | BP `abc` | HTTP 400, blood_pressure error | Pass |
| V3 | HbA1c 99 | HTTP 400, hba1c error | Pass |
| V4 | glucose -5 | HTTP 400 | Pass |
| V5 | hemoglobin `"low"` | HTTP 400 | Pass |
| V6 | temperature 80 | HTTP 400 | Pass |
| V7 | three invalid fields | HTTP 400, three field errors | Pass |
| V8 | non-JSON body | HTTP 400 | Pass |
| H1 | GET /api/health | HTTP 200, online | Pass |
| H2 | unknown route | HTTP 404 | Pass |

## New-condition tests (boundaries included)

| ID | Input | Result |
|---|---|---|
| N1 | glucose 110, HbA1c 6.0 | Prediabetes 100 |
| N2-N4 | glucose 110 / 99 / 100 | Prediabetes 44.4 / none / Prediabetes 44.4 |
| N5-N7 | HbA1c 5.7 / 6.4 / 6.5 | Prediabetes 55.6 / Prediabetes 55.6 / Type 2 Diabetes 55.6 |
| N8-N9 | TSH 0.2 / 0.4 | Hyperthyroidism 100 / none |
| N10-N12 | BP 85/55, 85/70, 90/60 | Hypotension 100, Hypotension 57.1, none |
| N13 | platelets 100 | Thrombocytopenia 100, Dengue 57.1 |
| N14-N15 | platelets 500 / 450 | Thrombocytosis 100 / none |
| N16 | WBC 15 | Bacterial Infection 57.1 |
| N17 | WBC 3 | Leukopenia 100 |
| N18-N19 | Hb 18 / 17 | Polycythemia 100 / none |
| N20-N21 | glucose 55 / 70 | Hypoglycemia 100 / none |
| N22 | 103 °F + platelets 100 | Dengue 100, Thrombocytopenia 100, Bacterial Infection 42.9 |
| N23 | 103 °F + Hb 10 | Malaria 100, Iron-Deficiency Anemia 100, Dengue 42.9, Bacterial Infection 42.9 |
| N24 | glucose 110, TSH 0.2, platelets 100 | Prediabetes 44.4, Hyperthyroidism 100, Thrombocytopenia 100, Dengue 57.1 |

Note: a fever alone matches Dengue and Bacterial Infection at 42.9. These are
non-specific rule matches, not diagnoses.

## Temperature tests (web form uses °F; the API also accepts °C)

| ID | Input | Result |
|---|---|---|
| F1 | 98.6 °F | normal |
| F2 | 100.3 °F | normal |
| F3 | 100.4 °F (boundary) | abnormal, Dengue 42.9 |
| F4 | 102 °F + platelets 60 | abnormal, Dengue 100 |
| F5 | 39.5 °C with unit C | abnormal, shown in °C |
| F6 | 101 with no unit sent | treated as °F, abnormal |
| F7 | 150 °F or 40 °F | HTTP 400, "between 86 and 113 °F" |
| F8 | `abc` | HTTP 400, valid number required |

## Web-form payload test

The web form sends `blood_pressure` and `fasting_glucose`. The backend
accepts both these names and its own `bloodPressure` / `fastingGlucose`.
With the form's exact payload (8 values) all 8 parameters are analysed.

## Open Targets integration (simulated responses)

| Case | Result |
|---|---|
| Normal response | Targets returned with symbol, name, score, Ensembl ID |
| HTTP 400 from API | Error logged, analysis still returned, 0 research records |
| Network failure | Error logged, analysis still returned, 0 research records |

## Network graph tests (headless DOM)

| Case | Result |
|---|---|
| Render with live-shaped data (7 conditions, 15 records) | 7 tabs, first active, 8 nodes for Type 2 Diabetes |
| Click Open Targets node | Panel shows name, score, Ensembl ID, link |
| Click curated-only node | Panel explains it is a curated example |
| Switch tab | Graph and summary change |
| No Open Targets records | Curated genes still drawn, explanatory message |
| No associations | Network section hidden |
| Hostile gene name / bad ID | Shown as plain text, no link created |

## Known limitations

- Scores are rule-match scores, not probabilities.
- Thresholds are prototype values and should be referenced to a guideline
  (for example WHO or ADA) in the report.
- Several conditions share parameters, so one abnormal value can match more
  than one condition.
- Gene and target lists in the knowledge base are curated examples.
