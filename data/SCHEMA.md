# Cliniq Data Schema

## patients.csv
patient_id, name, age, gender, condition, ward, floor, admission_date, release_date, doctor_assigned

## vitals.csv
patient_id, date, systolic_bp, diastolic_bp, pulse_rate, spo2

One row per patient per day of stay (admission_date through min(release_date, today)).

## appointments.csv
appointment_id, patient_id, date, doctor, type
type in {Post-Surgical Care, Consultation, Follow-up}. 3 appointments per patient.

## diagnoses.csv
diagnosis_id, patient_id, diagnosis, severity, requires_surgery, potential_release_date
severity in {Mild, Moderate, Severe, Critical}.
