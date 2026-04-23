# Cliniq EDA — Key Findings

- **Cohort**: 500 patients (257 female, 243 male), mean age 47.3 years.
- **Admission window**: 2026-02-22 to 2026-04-23.

## Condition Mix
- Cardiology: 114 (23%)
- Cancer: 89 (18%)
- Diabetes: 89 (18%)
- Anxiety Disorder: 83 (17%)
- Behavioral Issues: 67 (13%)
- Anesthesiology: 58 (12%)

## Top 5 Diagnoses
- Angina: 29
- Colorectal Cancer: 27
- Diabetic Ketoacidosis: 27
- Myocardial Infarction: 24
- Panic Disorder: 23

## Average Vitals by Condition
| condition | systolic_bp | diastolic_bp | pulse_rate | spo2 |
|---|---|---|---|---|
| Anesthesiology | 123.6 | 77.1 | 70.2 | 96.3 |
| Anxiety Disorder | 125.0 | 75.4 | 85.2 | 97.3 |
| Behavioral Issues | 119.0 | 74.7 | 79.3 | 97.0 |
| Cancer | 131.8 | 78.5 | 83.4 | 93.9 |
| Cardiology | 147.0 | 87.0 | 84.4 | 96.5 |
| Diabetes | 132.7 | 81.4 | 75.3 | 96.9 |

## Surgery Requirement
- Anesthesiology: 91%
- Cancer: 62%
- Cardiology: 46%
- Diabetes: 8%
- Behavioral Issues: 3%
- Anxiety Disorder: 0%

## Age by Condition
| condition | mean | median | min | max |
|---|---|---|---|---|
| Anesthesiology | 43.1 | 43.0 | 18.0 | 73.0 |
| Anxiety Disorder | 33.1 | 34.0 | 6.0 | 59.0 |
| Behavioral Issues | 27.8 | 28.0 | 8.0 | 45.0 |
| Cancer | 56.6 | 56.0 | 25.0 | 92.0 |
| Cardiology | 61.2 | 62.0 | 11.0 | 92.0 |
| Diabetes | 50.9 | 49.0 | 6.0 | 81.0 |

## Severity Distribution
- Mild: 122
- Moderate: 202
- Severe: 135
- Critical: 41

## Headline Observations
- **Highest avg systolic BP**: Cardiology (147.0 mmHg).
- **Lowest avg SpO2**: Cancer (93.9%).
- **Highest avg pulse**: Anxiety Disorder (85.2 bpm).
- **Most surgery-heavy condition**: Anesthesiology (91%).
- **Critical cases**: 41 (8.2%).
