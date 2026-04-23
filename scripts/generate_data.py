"""Cliniq data-engineer: synthetic hospital dataset generator.

Outputs to /data:
  - patients.csv
  - vitals.csv
  - appointments.csv
  - diagnoses.csv
  - SCHEMA.md
"""
from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

N_PATIENTS = 500
APPTS_PER_PATIENT = 3
TODAY = date(2026, 4, 23)

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Kabir", "Ayaan", "Dhruv", "Kian", "Rudra", "Aryan",
    "Ananya", "Diya", "Aadhya", "Saanvi", "Pari", "Myra", "Anika", "Navya",
    "Kiara", "Ira", "Siya", "Riya", "Aisha", "Zara", "Meera", "Tara",
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Liam", "Noah", "Oliver", "Emma", "Sophia", "Isabella", "Mia", "Charlotte",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Reddy", "Iyer",
    "Nair", "Menon", "Das", "Roy", "Bose", "Mehta", "Shah", "Joshi",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
]

DOCTORS = [
    ("Dr. Anita Rao", "Cardiology"),
    ("Dr. Rajesh Kumar", "Cardiology"),
    ("Dr. Meera Iyer", "Oncology"),
    ("Dr. Samuel Chen", "Oncology"),
    ("Dr. Priya Nair", "Psychiatry"),
    ("Dr. Arvind Menon", "Psychiatry"),
    ("Dr. Neha Gupta", "Endocrinology"),
    ("Dr. Thomas Wright", "Endocrinology"),
    ("Dr. Lakshmi Rao", "Anesthesiology"),
    ("Dr. David Park", "Anesthesiology"),
    ("Dr. Kavita Joshi", "Behavioral Health"),
    ("Dr. Michael Green", "Behavioral Health"),
    ("Dr. Sunita Verma", "General Medicine"),
    ("Dr. Rohan Desai", "General Surgery"),
]

# condition -> (department, ward, floor, typical_severity_weights, surgery_prob, stay_days_range)
CONDITIONS = {
    "Cardiology": {
        "ward": "Cardiac Care Unit",
        "floor": 3,
        "diagnoses": ["Myocardial Infarction", "Hypertension", "Arrhythmia", "Congestive Heart Failure", "Angina"],
        "severity_weights": {"Mild": 0.15, "Moderate": 0.45, "Severe": 0.30, "Critical": 0.10},
        "surgery_prob": 0.35,
        "stay": (4, 14),
    },
    "Anxiety Disorder": {
        "ward": "Psychiatric Ward",
        "floor": 5,
        "diagnoses": ["Generalized Anxiety Disorder", "Panic Disorder", "Social Anxiety", "PTSD"],
        "severity_weights": {"Mild": 0.45, "Moderate": 0.40, "Severe": 0.13, "Critical": 0.02},
        "surgery_prob": 0.0,
        "stay": (2, 10),
    },
    "Cancer": {
        "ward": "Oncology Ward",
        "floor": 4,
        "diagnoses": ["Breast Cancer", "Lung Cancer", "Colorectal Cancer", "Leukemia", "Lymphoma"],
        "severity_weights": {"Mild": 0.05, "Moderate": 0.30, "Severe": 0.45, "Critical": 0.20},
        "surgery_prob": 0.55,
        "stay": (5, 21),
    },
    "Diabetes": {
        "ward": "Endocrinology Ward",
        "floor": 2,
        "diagnoses": ["Type 1 Diabetes", "Type 2 Diabetes", "Diabetic Ketoacidosis", "Gestational Diabetes"],
        "severity_weights": {"Mild": 0.25, "Moderate": 0.50, "Severe": 0.20, "Critical": 0.05},
        "surgery_prob": 0.08,
        "stay": (2, 8),
    },
    "Anesthesiology": {
        "ward": "Surgical Recovery",
        "floor": 1,
        "diagnoses": ["Post-Operative Recovery", "Anesthesia Complication", "Pre-Surgical Evaluation"],
        "severity_weights": {"Mild": 0.30, "Moderate": 0.50, "Severe": 0.18, "Critical": 0.02},
        "surgery_prob": 0.90,
        "stay": (1, 7),
    },
    "Behavioral Issues": {
        "ward": "Behavioral Health Unit",
        "floor": 5,
        "diagnoses": ["Bipolar Disorder", "Major Depression", "ADHD", "Conduct Disorder", "OCD"],
        "severity_weights": {"Mild": 0.35, "Moderate": 0.40, "Severe": 0.20, "Critical": 0.05},
        "surgery_prob": 0.0,
        "stay": (3, 14),
    },
}

CONDITION_LIST = list(CONDITIONS.keys())
CONDITION_WEIGHTS = [0.22, 0.14, 0.18, 0.18, 0.14, 0.14]

APPT_TYPES = ["Post-Surgical Care", "Consultation", "Follow-up"]


def weighted_choice(options: dict[str, float]) -> str:
    keys = list(options.keys())
    weights = list(options.values())
    return random.choices(keys, weights=weights, k=1)[0]


def doctor_for(condition: str) -> str:
    mapping = {
        "Cardiology": "Cardiology",
        "Anxiety Disorder": "Psychiatry",
        "Cancer": "Oncology",
        "Diabetes": "Endocrinology",
        "Anesthesiology": "Anesthesiology",
        "Behavioral Issues": "Behavioral Health",
    }
    dept = mapping[condition]
    matches = [d for d, spec in DOCTORS if spec == dept]
    return random.choice(matches)


def vitals_for(age: int, condition: str, severity: str) -> tuple[int, int, int, int]:
    """Return (systolic, diastolic, pulse, spo2) with clinical realism."""
    sys_base = 115 + max(0, (age - 30)) * 0.4
    dia_base = 75 + max(0, (age - 30)) * 0.15
    pulse_base = 72
    spo2_base = 98

    if condition == "Cardiology":
        sys_base += 15
        dia_base += 8
        pulse_base += 8
    elif condition == "Anxiety Disorder":
        pulse_base += 12
        sys_base += 6
    elif condition == "Cancer":
        pulse_base += 5
        spo2_base -= 2
    elif condition == "Diabetes":
        sys_base += 6
        dia_base += 3
    elif condition == "Anesthesiology":
        pulse_base -= 4
        spo2_base -= 1
    elif condition == "Behavioral Issues":
        pulse_base += 4

    sev_bump = {"Mild": 0, "Moderate": 3, "Severe": 7, "Critical": 12}[severity]
    sys_base += sev_bump
    pulse_base += sev_bump
    spo2_base -= sev_bump * 0.3

    systolic = int(random.gauss(sys_base, 7))
    diastolic = int(random.gauss(dia_base, 5))
    pulse = int(random.gauss(pulse_base, 6))
    spo2 = int(round(random.gauss(spo2_base, 1.2)))

    systolic = max(85, min(210, systolic))
    diastolic = max(50, min(130, diastolic))
    pulse = max(45, min(160, pulse))
    spo2 = max(82, min(100, spo2))
    return systolic, diastolic, pulse, spo2


def gen_patients() -> list[dict]:
    patients = []
    for i in range(1, N_PATIENTS + 1):
        pid = f"P{i:06d}"
        gender = random.choices(["Male", "Female"], weights=[0.49, 0.51])[0]
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"

        condition = random.choices(CONDITION_LIST, weights=CONDITION_WEIGHTS, k=1)[0]
        cfg = CONDITIONS[condition]

        if condition == "Behavioral Issues":
            age = random.randint(8, 45)
        elif condition == "Cardiology":
            age = int(random.gauss(62, 12))
        elif condition == "Cancer":
            age = int(random.gauss(58, 15))
        elif condition == "Diabetes":
            age = int(random.gauss(52, 14))
        elif condition == "Anxiety Disorder":
            age = int(random.gauss(35, 12))
        else:
            age = int(random.gauss(45, 15))
        age = max(6, min(92, age))

        stay_days = random.randint(*cfg["stay"])
        admission = TODAY - timedelta(days=random.randint(0, 60))
        release = admission + timedelta(days=stay_days)

        patients.append({
            "patient_id": pid,
            "name": name,
            "age": age,
            "gender": gender,
            "condition": condition,
            "ward": cfg["ward"],
            "floor": cfg["floor"],
            "admission_date": admission.isoformat(),
            "release_date": release.isoformat(),
            "doctor_assigned": doctor_for(condition),
        })
    return patients


def gen_vitals(patients: list[dict]) -> list[dict]:
    rows = []
    for p in patients:
        admission = date.fromisoformat(p["admission_date"])
        release = date.fromisoformat(p["release_date"])
        last_day = min(release, TODAY)
        severity_placeholder = "Moderate"
        day = admission
        while day <= last_day:
            s, d, pulse, spo2 = vitals_for(p["age"], p["condition"], severity_placeholder)
            rows.append({
                "patient_id": p["patient_id"],
                "date": day.isoformat(),
                "systolic_bp": s,
                "diastolic_bp": d,
                "pulse_rate": pulse,
                "spo2": spo2,
            })
            day += timedelta(days=1)
    return rows


def gen_appointments(patients: list[dict]) -> list[dict]:
    rows = []
    appt_counter = 1
    for p in patients:
        admission = date.fromisoformat(p["admission_date"])
        release = date.fromisoformat(p["release_date"])
        had_surgery = p["condition"] in ("Cardiology", "Cancer", "Anesthesiology")
        types_pool = APPT_TYPES.copy()
        if not had_surgery:
            types_pool = ["Consultation", "Follow-up", "Consultation"]

        for k in range(APPTS_PER_PATIENT):
            if k == 0:
                appt_date = admission + timedelta(days=random.randint(0, 2))
                a_type = "Consultation"
            elif k == 1:
                span = max(1, (release - admission).days)
                appt_date = admission + timedelta(days=random.randint(1, span))
                a_type = random.choice(types_pool)
            else:
                appt_date = release + timedelta(days=random.randint(3, 21))
                a_type = "Follow-up" if random.random() < 0.6 else random.choice(types_pool)

            rows.append({
                "appointment_id": f"A{appt_counter:07d}",
                "patient_id": p["patient_id"],
                "date": appt_date.isoformat(),
                "doctor": p["doctor_assigned"],
                "type": a_type,
            })
            appt_counter += 1
    return rows


def gen_diagnoses(patients: list[dict]) -> list[dict]:
    rows = []
    diag_counter = 1
    for p in patients:
        cfg = CONDITIONS[p["condition"]]
        severity = weighted_choice(cfg["severity_weights"])
        diagnosis = random.choice(cfg["diagnoses"])
        requires_surgery = random.random() < cfg["surgery_prob"]
        if severity == "Critical":
            requires_surgery = requires_surgery or random.random() < 0.4

        release = date.fromisoformat(p["release_date"])
        extra = {"Mild": -1, "Moderate": 1, "Severe": 4, "Critical": 8}[severity]
        if requires_surgery:
            extra += random.randint(2, 5)
        potential_release = release + timedelta(days=extra)

        rows.append({
            "diagnosis_id": f"D{diag_counter:07d}",
            "patient_id": p["patient_id"],
            "diagnosis": diagnosis,
            "severity": severity,
            "requires_surgery": requires_surgery,
            "potential_release_date": potential_release.isoformat(),
        })
        diag_counter += 1
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_schema() -> None:
    schema = """# Cliniq Data Schema

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
"""
    (DATA / "SCHEMA.md").write_text(schema, encoding="utf-8")


def main() -> None:
    patients = gen_patients()
    write_csv(
        DATA / "patients.csv",
        patients,
        ["patient_id", "name", "age", "gender", "condition", "ward", "floor",
         "admission_date", "release_date", "doctor_assigned"],
    )

    diagnoses = gen_diagnoses(patients)
    write_csv(
        DATA / "diagnoses.csv",
        diagnoses,
        ["diagnosis_id", "patient_id", "diagnosis", "severity",
         "requires_surgery", "potential_release_date"],
    )

    sev_by_pid = {d["patient_id"]: d["severity"] for d in diagnoses}
    vitals = []
    for p in patients:
        admission = date.fromisoformat(p["admission_date"])
        release = date.fromisoformat(p["release_date"])
        last_day = min(release, TODAY)
        sev = sev_by_pid[p["patient_id"]]
        day = admission
        while day <= last_day:
            s, d, pulse, spo2 = vitals_for(p["age"], p["condition"], sev)
            vitals.append({
                "patient_id": p["patient_id"],
                "date": day.isoformat(),
                "systolic_bp": s,
                "diastolic_bp": d,
                "pulse_rate": pulse,
                "spo2": spo2,
            })
            day += timedelta(days=1)
    write_csv(
        DATA / "vitals.csv",
        vitals,
        ["patient_id", "date", "systolic_bp", "diastolic_bp", "pulse_rate", "spo2"],
    )

    appointments = gen_appointments(patients)
    write_csv(
        DATA / "appointments.csv",
        appointments,
        ["appointment_id", "patient_id", "date", "doctor", "type"],
    )

    write_schema()

    print(f"patients:     {len(patients)}")
    print(f"vitals:       {len(vitals)}")
    print(f"appointments: {len(appointments)}")
    print(f"diagnoses:    {len(diagnoses)}")
    print(f"written to:   {DATA}")


if __name__ == "__main__":
    main()
