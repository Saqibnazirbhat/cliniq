"""Cliniq eda-agent: exploratory data analysis.

Loads /data CSVs, writes charts + aggregates to /eda, prints a summary.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EDA = ROOT / "eda"
EDA.mkdir(parents=True, exist_ok=True)

CLINICAL_BLUE = "#1f77b4"
CLINICAL_TEAL = "#2a9d8f"
CLINICAL_RED = "#d62828"
PALETTE = ["#1f77b4", "#2a9d8f", "#e9c46a", "#f4a261", "#d62828", "#6a4c93"]

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "font.size": 10,
})


def df_to_md(df: pd.DataFrame) -> str:
    idx_name = df.index.name or ""
    cols = [idx_name] + [str(c) for c in df.columns]
    head = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join(["---"] * len(cols)) + "|"
    rows = []
    for idx, row in df.iterrows():
        vals = [str(idx)] + [str(v) for v in row.values]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([head, sep] + rows)


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    patients = pd.read_csv(DATA / "patients.csv", parse_dates=["admission_date", "release_date"])
    vitals = pd.read_csv(DATA / "vitals.csv", parse_dates=["date"])
    appts = pd.read_csv(DATA / "appointments.csv", parse_dates=["date"])
    diagnoses = pd.read_csv(DATA / "diagnoses.csv", parse_dates=["potential_release_date"])
    return patients, vitals, appts, diagnoses


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(EDA / name, bbox_inches="tight")
    plt.close(fig)


def chart_conditions(patients: pd.DataFrame) -> pd.Series:
    counts = patients["condition"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(counts.index, counts.values, color=PALETTE[: len(counts)])
    ax.set_title("Patient Distribution by Condition")
    ax.set_ylabel("Number of Patients")
    ax.tick_params(axis="x", rotation=20)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, str(v), ha="center", fontsize=9)
    save(fig, "01_condition_distribution.png")
    return counts


def chart_diagnoses(diagnoses: pd.DataFrame) -> pd.Series:
    top = diagnoses["diagnosis"].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top.index[::-1], top.values[::-1], color=CLINICAL_TEAL)
    ax.set_title("Top Diagnoses")
    ax.set_xlabel("Number of Patients")
    save(fig, "02_top_diagnoses.png")
    return top


def chart_avg_vitals(patients: pd.DataFrame, vitals: pd.DataFrame) -> pd.DataFrame:
    merged = vitals.merge(patients[["patient_id", "condition"]], on="patient_id")
    agg = merged.groupby("condition")[["systolic_bp", "diastolic_bp", "pulse_rate", "spo2"]].mean().round(1)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    metrics = [
        ("systolic_bp", "Avg Systolic BP (mmHg)", CLINICAL_RED),
        ("diastolic_bp", "Avg Diastolic BP (mmHg)", "#f4a261"),
        ("pulse_rate", "Avg Pulse Rate (bpm)", CLINICAL_BLUE),
        ("spo2", "Avg SpO2 (%)", CLINICAL_TEAL),
    ]
    for ax, (col, title, color) in zip(axes.flat, metrics):
        s = agg[col].sort_values()
        ax.barh(s.index, s.values, color=color)
        ax.set_title(title)
        if col == "spo2":
            ax.set_xlim(90, 100)
        for i, v in enumerate(s.values):
            ax.text(v, i, f" {v}", va="center", fontsize=8)
    fig.suptitle("Average Vitals by Condition", fontsize=13, fontweight="bold")
    save(fig, "03_avg_vitals_by_condition.png")
    return agg


def chart_admissions(patients: pd.DataFrame) -> pd.Series:
    daily = patients.groupby(patients["admission_date"].dt.date).size().sort_index()
    weekly = daily.resample("W", on=None).sum() if False else None  # keep it simple

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=False)

    ax1.plot(daily.index, daily.values, color=CLINICAL_BLUE, linewidth=1.2)
    ax1.fill_between(daily.index, daily.values, color=CLINICAL_BLUE, alpha=0.15)
    ax1.set_title("Daily Admissions")
    ax1.set_ylabel("Admissions")
    ax1.tick_params(axis="x", rotation=30)

    weekly_ser = patients.set_index("admission_date").resample("W").size()
    ax2.bar(weekly_ser.index, weekly_ser.values, width=5, color=CLINICAL_TEAL)
    ax2.set_title("Weekly Admissions")
    ax2.set_ylabel("Admissions")
    ax2.tick_params(axis="x", rotation=30)

    fig.suptitle("Admission Trends Over Time", fontsize=13, fontweight="bold")
    save(fig, "04_admission_trends.png")
    return daily


def chart_surgery(patients: pd.DataFrame, diagnoses: pd.DataFrame) -> pd.Series:
    merged = diagnoses.merge(patients[["patient_id", "condition"]], on="patient_id")
    merged["requires_surgery"] = merged["requires_surgery"].astype(str).str.lower().map(
        {"true": True, "false": False}
    )
    rate = merged.groupby("condition")["requires_surgery"].mean().sort_values(ascending=False) * 100
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [CLINICAL_RED if v > 50 else "#f4a261" if v > 20 else CLINICAL_TEAL for v in rate.values]
    bars = ax.bar(rate.index, rate.values, color=colors)
    ax.set_title("Surgery Requirement Rate by Condition")
    ax.set_ylabel("% of Patients Requiring Surgery")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=20)
    for b, v in zip(bars, rate.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%", ha="center", fontsize=9)
    save(fig, "05_surgery_rate_by_condition.png")
    return rate


def chart_age_by_condition(patients: pd.DataFrame) -> pd.DataFrame:
    fig, ax = plt.subplots(figsize=(9, 5.5))
    conditions = sorted(patients["condition"].unique())
    data = [patients.loc[patients["condition"] == c, "age"].values for c in conditions]
    bp = ax.boxplot(data, tick_labels=conditions, patch_artist=True, medianprops={"color": "black"})
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_title("Patient Age Distribution by Condition")
    ax.set_ylabel("Age (years)")
    ax.tick_params(axis="x", rotation=20)
    save(fig, "06_age_by_condition.png")

    summary = patients.groupby("condition")["age"].agg(["mean", "median", "min", "max"]).round(1)
    return summary


def chart_severity(diagnoses: pd.DataFrame) -> pd.Series:
    order = ["Mild", "Moderate", "Severe", "Critical"]
    counts = diagnoses["severity"].value_counts().reindex(order).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(counts.index, counts.values, color=[CLINICAL_TEAL, "#e9c46a", "#f4a261", CLINICAL_RED])
    ax.set_title("Severity Distribution")
    ax.set_ylabel("Number of Patients")
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, str(v), ha="center", fontsize=9)
    save(fig, "07_severity_distribution.png")
    return counts


def write_summary(
    patients: pd.DataFrame,
    cond_counts: pd.Series,
    top_dx: pd.Series,
    vitals_agg: pd.DataFrame,
    surgery_rate: pd.Series,
    age_summary: pd.DataFrame,
    severity_counts: pd.Series,
) -> str:
    total = len(patients)
    female = (patients["gender"] == "Female").sum()
    male = total - female
    avg_age = patients["age"].mean()
    date_range = (patients["admission_date"].min().date(), patients["admission_date"].max().date())

    lines = []
    lines.append("# Cliniq EDA — Key Findings\n")
    lines.append(f"- **Cohort**: {total} patients ({female} female, {male} male), mean age {avg_age:.1f} years.")
    lines.append(f"- **Admission window**: {date_range[0]} to {date_range[1]}.\n")

    lines.append("## Condition Mix")
    for c, n in cond_counts.items():
        lines.append(f"- {c}: {n} ({n/total:.0%})")

    lines.append("\n## Top 5 Diagnoses")
    for d, n in top_dx.head(5).items():
        lines.append(f"- {d}: {n}")

    lines.append("\n## Average Vitals by Condition")
    lines.append(df_to_md(vitals_agg))

    lines.append("\n## Surgery Requirement")
    for c, r in surgery_rate.items():
        lines.append(f"- {c}: {r:.0f}%")

    lines.append("\n## Age by Condition")
    lines.append(df_to_md(age_summary))

    lines.append("\n## Severity Distribution")
    for s, n in severity_counts.items():
        lines.append(f"- {s}: {n}")

    hi_bp = vitals_agg["systolic_bp"].idxmax()
    lo_spo2 = vitals_agg["spo2"].idxmin()
    hi_pulse = vitals_agg["pulse_rate"].idxmax()
    top_surg = surgery_rate.idxmax()

    lines.append("\n## Headline Observations")
    lines.append(f"- **Highest avg systolic BP**: {hi_bp} ({vitals_agg.loc[hi_bp, 'systolic_bp']} mmHg).")
    lines.append(f"- **Lowest avg SpO2**: {lo_spo2} ({vitals_agg.loc[lo_spo2, 'spo2']}%).")
    lines.append(f"- **Highest avg pulse**: {hi_pulse} ({vitals_agg.loc[hi_pulse, 'pulse_rate']} bpm).")
    lines.append(f"- **Most surgery-heavy condition**: {top_surg} ({surgery_rate[top_surg]:.0f}%).")
    lines.append(f"- **Critical cases**: {severity_counts.get('Critical', 0)} ({severity_counts.get('Critical', 0)/total:.1%}).")

    report = "\n".join(lines) + "\n"
    (EDA / "summary.md").write_text(report, encoding="utf-8")
    return report


def main() -> None:
    patients, vitals, appts, diagnoses = load()

    cond_counts = chart_conditions(patients)
    top_dx = chart_diagnoses(diagnoses)
    vitals_agg = chart_avg_vitals(patients, vitals)
    chart_admissions(patients)
    surgery_rate = chart_surgery(patients, diagnoses)
    age_summary = chart_age_by_condition(patients)
    severity_counts = chart_severity(diagnoses)

    vitals_agg.to_csv(DATA / "vitals_by_condition_agg.csv")
    surgery_rate.round(1).to_csv(DATA / "surgery_rate_agg.csv", header=["surgery_rate_pct"])

    report = write_summary(patients, cond_counts, top_dx, vitals_agg, surgery_rate, age_summary, severity_counts)

    print(report)
    print(f"\n[charts written to {EDA}]")


if __name__ == "__main__":
    main()
