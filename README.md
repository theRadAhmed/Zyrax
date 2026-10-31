# ZyraX

**Biomedical Analysis Prototype (v2.1)**
M.Sc. Bioinformatics minor project, Jamia Millia Islamia.

ZyraX connects clinical-style parameters to disease associations and to
disease-associated molecular targets retrieved from the Open Targets
Platform.

> **ZyraX is an academic research prototype. It is not a medical device and
> cannot diagnose conditions or recommend treatment.**

## Workflow

```
Lab parameters -> rule-based abnormality flags -> disease associations
               -> genes / targets (curated) + Open Targets evidence
```

## Features

- Eight optional parameters: blood pressure, fasting glucose, HbA1c,
  hemoglobin, TSH, temperature, platelets, WBC
- Temperature entered in °F (as commonly used in India); rules run internally in °C
- Easy entry: one-click example fills, live range hints under each field, unit toggles (glucose mg/dL or mmol/L, hemoglobin g/dL or g/L, temperature °F or °C), flexible blood pressure format (120/80, 120 80), value counter
- Input validation with per-field error messages
- Rule-based abnormality flags
- Fifteen condition profiles: Type 2 Diabetes, Prediabetes, Hypoglycemia,
  Iron-Deficiency Anemia, Hypothyroidism, Hyperthyroidism, Hypertension,
  Hypotension, Thrombocytopenia, Thrombocytosis, Leukopenia, Polycythemia,
  Bacterial Infection, Dengue, Malaria
- Two-sided reference ranges (low and high) for every parameter
- Export: "Download PDF report" (via the browser's Save as PDF) and "Copy summary text", with optional name/age/sex printed only on the report
- Per-disease rule-match score and the parameters that triggered it
- Interactive Disease-Gene-Target network: curated genes versus Open Targets
  targets for each matched condition, with association scores and links
- Live research section: top disease-associated targets (gene symbol,
  name, association score) from Open Targets
- If Open Targets is unreachable, the analysis still works and the
  research section is simply empty

## Requirements

- Python 3.9+
- Packages: Flask, Flask-CORS, requests (see `requirements.txt`)
- Internet access for the research section

## Run

```bash
cd <project folder>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> and click **Start Analysis**.

## Check the Open Targets connection

```bash
python check_open_targets.py
```

## API

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Homepage |
| `/analysis` | GET | Analysis interface |
| `/api/health` | GET | Service status |
| `/api/analyze` | POST | Analyse parameters (JSON body) |

Example request body (all fields optional, at least one required):

```json
{
  "bloodPressure": "120/80",
  "fastingGlucose": 140,
  "hba1c": 7.2,
  "hemoglobin": 11,
  "tsh": 5.2,
  "temperature": 98.6,
  "temperature_unit": "F",
  "platelets": 250,
  "wbc": 7.5
}
```

Response keys: `summary`, `parameters`, `associations` (also `results`),
`research_records` (also `research_results`), `prototype_notice`.
Validation failures return HTTP 400 with `validation_errors`
(field -> message).

## Method and limitations

1. **Rule-based flags.** Each value is compared with fixed prototype
   ranges, low and high (see table below). These are simple cut-offs, not
   clinically validated decision rules. Reference them to a guideline
   (for example WHO or ADA) in your report.

   | Parameter | Prototype range | Flagged |
   |---|---|---|
   | Blood pressure | 90/60 to 130/80 mmHg | above or below |
   | Fasting glucose | 70-99 mg/dL | < 70, 100-125 borderline, >= 126 high |
   | HbA1c | < 5.7 % | 5.7-6.4 borderline, >= 6.5 high |
   | Hemoglobin | 12-17 g/dL | below or above |
   | TSH | 0.4-4.5 mIU/L | below or above |
   | Temperature | < 100.4 °F (38 °C) | fever at or above |
   | Platelets | 150-450 ×10³/µL | below or above |
   | WBC | 4-11 ×10³/µL | below or above |
2. **Disease associations.** Each disease has weighted rules. The score is
   the share of that disease's rule weight that matched. It is a
   **rule-match score, not a probability**, and a single abnormal value can
   produce a partial score.
3. **Genes and targets.** The gene and target lists in `app.py` are curated
   examples for demonstration.
4. **Network view.** For each matched condition, the graph shows curated
   example genes (left) and top Open Targets targets (right, line thickness =
   association score). A ringed node is in both lists. An edge shows an
   association in the data, not causation or an available treatment.
5. **Open Targets evidence.** Targets are retrieved live from the Open
   Targets GraphQL API and ranked by their association score. A retrieved
   association is research evidence, not clinical validation.

## Project structure

```
app.py                    Flask backend, rules, Open Targets client
analysis.html             Analysis interface
index.html                Homepage
check_open_targets.py     Live API check (all diseases)
find_disease_ids.py       Lists Open Targets disease ID candidates
requirements.txt
TESTING.md                Test cases and results
archive_old_versions/     Earlier frontend files (not used by the app)
```

## Data source

Open Targets Platform: <https://platform.opentargets.org>
Cite the relevant Open Targets publication and data release in your report.

- **Upload a lab report:** choose a PDF or photo of a blood test report; ZyraX reads the text in the browser (PDF.js / Tesseract.js, loaded from a CDN when needed), fills the matching fields, and you check them before analysing. ECG and MRI/CT images are not interpreted.

- **Explain my report (optional, AI):** hidden unless `ANTHROPIC_API_KEY` is set. After uploading a report (PDF/photo), tick the consent box and press *Explain this report with AI*. The file is sent through the Flask server (`POST /api/explain`) to the Claude API and a plain-language explanation comes back. It never diagnoses. Needs an API key: `export ANTHROPIC_API_KEY=your_key` before `python3 app.py` (optional `ZYRAX_MODEL`). Limits: 8 MB, PDF/PNG/JPEG/WebP, 12 requests per hour per user.

- **Gene biology panel:** for each matched condition, shows each gene's protein name and function (UniProt), its interaction partners, a small interaction network between the condition's genes and the pathways they share (STRING). No API key; the Flask server calls the public UniProt and STRING APIs (`GET /api/genes?symbols=...`). Results are cached in memory.
