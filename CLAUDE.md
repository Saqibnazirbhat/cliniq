# Cliniq

Healthcare patient management dashboard system. This file is the shared spec for all subagents.

## Project Overview

Cliniq is an end-to-end synthetic healthcare analytics pipeline that generates patient data, explores it, and surfaces it through a clinical-style interactive dashboard.

## Directory Layout

- `/data` — all generated datasets (CSV/JSON/Parquet). Single source of truth for downstream agents.
- `/eda` — exploratory data analysis outputs: charts (PNG/SVG), notebooks, and summary reports.
- `/dashboard` — the interactive dashboard application (HTML/JS or Streamlit/Dash) styled as a clinical patient management UI.

## Subagents

Three specialized subagents collaborate on the pipeline. Each reads this CLAUDE.md as its spec.

### 1. `data-engineer`
Generates synthetic patient data. Outputs to `/data`.

Required datasets:
- **Demographics** — patient_id, name, age, sex, contact, address, insurance, blood group.
- **Vitals** — patient_id, timestamp, heart_rate, blood_pressure (sys/dia), temperature, SpO2, respiratory_rate, BMI.
- **Appointments** — appointment_id, patient_id, provider, department, scheduled_at, status (scheduled/completed/no-show/cancelled).
- **Diagnoses** — diagnosis_id, patient_id, ICD-10 code, description, diagnosed_at, severity, chronic flag.

Realism requirements: correlate vitals with age/conditions, keep ranges clinically plausible, include longitudinal records per patient, seed RNG for reproducibility.

### 2. `eda-agent`
Explores patterns in the `/data` outputs. Writes charts and summaries to `/eda`.

Required analyses:
- Most common conditions / ICD-10 frequency.
- Vitals distributions (histograms, box plots) broken down by age group and sex.
- Admission / appointment trends over time (daily, weekly, monthly; no-show rates by department).
- Comorbidity co-occurrence (chronic conditions).
- Abnormal-vitals flagging (values outside clinical reference ranges).

Deliverables: labeled charts, a `summary.md` with key findings, and any derived/aggregated tables saved back to `/data` as `*_agg.csv`.

### 3. `dashboard-agent`
Builds the interactive dashboard in `/dashboard`, consuming `/data` and `/eda`.

UI requirements — styled as a clinical patient management system:
- Patient roster with search, filters (age, sex, department, chronic flag), and selectable rows.
- Patient detail view: demographics card, vitals trend charts, appointment history, diagnosis list with severity badges.
- Population view: KPIs (total patients, appointments today, no-show rate, top diagnoses) and trend charts sourced from `/eda`.
- Clinical aesthetic: clean whites/blues, readable typography, status badges, accessible contrast.

Prefer Streamlit, Dash, or a single-page static site with Chart.js/Plotly. Must run with a single documented command.

## Shared Conventions

- All timestamps ISO 8601, UTC.
- Patient IDs: `P` + zero-padded 6-digit integer (e.g., `P000123`).
- File names lowercase snake_case (e.g., `patients_demographics.csv`).
- Every agent starts by reading `/data` to discover schemas — never hardcode column names beyond those defined above.
- Changes to schemas must be reflected in a `/data/SCHEMA.md` maintained by `data-engineer`.

## Pipeline Order

`data-engineer` → `eda-agent` → `dashboard-agent`. Later stages must not mutate earlier outputs.
