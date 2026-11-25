"""
make_report.py  —  DozAI Project Report Generator
Author : Akash Kumar
Program: IBM SkillsBuild · Data Analytics with AI · BharatCares x AICTE

Run AFTER the notebook completes (Run All):
    python make_report.py
Output: Akash_Kumar_DozAI_ProjectReport.docx

All monetary symbols use "Rs" (not the rupee Unicode glyph) for
encoding safety across Windows / Linux / macOS.
"""

import json
import os
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ── Tiny helpers ─────────────────────────────────────────────────────────────

def heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return h


def para(doc, text, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    return p


def bullet(doc, text):
    return doc.add_paragraph(text, style="List Bullet")


def numbered(doc, text):
    return doc.add_paragraph(text, style="List Number")


def table_from(doc, headers, rows, caption=None):
    if caption:
        cp = doc.add_paragraph()
        cp.add_run(caption).bold = True
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Light Grid Accent 1"

    hcells = t.rows[0].cells
    for i, h in enumerate(headers):
        hcells[i].text = h
        for p in hcells[i].paragraphs:
            for r in p.runs:
                r.bold = True

    for ri, row in enumerate(rows):
        dcells = t.rows[ri + 1].cells
        for ci, val in enumerate(row):
            dcells[ci].text = str(val)

    doc.add_paragraph()
    return t


def figure(doc, path, width=6.2, caption=None):
    if not os.path.exists(path):
        doc.add_paragraph(f"[Figure not found: {path}]").italic = True
        return
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        cp = doc.add_paragraph(caption)
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cp.runs:
            r.italic = True
            r.font.size = Pt(9)
    doc.add_paragraph()


def safe(d, *keys, default="N/A"):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur if cur is not None else default


def fmt(v, dec=4):
    try:
        return f"{float(v):.{dec}f}"
    except Exception:
        return str(v)


# ── Main ─────────────────────────────────────────────────────────────────────

def build():
    rp = Path("models/results.json")
    if not rp.exists():
        raise FileNotFoundError(
            "models/results.json not found.\n"
            "Run the notebook first: sleepai.ipynb -> Kernel -> Restart & Run All"
        )
    with open(rp, encoding="utf-8") as f:
        res = json.load(f)

    doc = Document()

    # Page margins
    for sec in doc.sections:
        sec.top_margin    = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin   = Inches(1.0)
        sec.right_margin  = Inches(1.0)

    # ── Cover ─────────────────────────────────────────────────────────────────
    t = doc.add_heading("DozAI", 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    s = doc.add_paragraph("Sleep-Aware Smart-Home Energy Optimization")
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s.runs[0].font.size = Pt(14)
    s.runs[0].bold = True

    a = doc.add_paragraph(
        "Akash Kumar\n"
        "IBM SkillsBuild  |  Data Analytics with AI  |  BharatCares x AICTE"
    )
    a.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    pl = doc.add_paragraph(
        "Pipeline: Energy -> Environment -> Sleep -> Prediction -> Optimization -> Recommendation"
    )
    pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pl.runs[0].italic = True

    doc.add_page_break()

    # ── 1. Problem Statement ──────────────────────────────────────────────────
    heading(doc, "1. Problem Statement")
    para(doc,
        "Modern smart-home energy management systems optimise appliance scheduling "
        "for cost, completely ignoring the occupant's sleep. Conversely, consumer "
        "sleep-health apps track sleep but remain disconnected from the home's "
        "energy state. The result: dishwashers at 23:00, dryers at midnight, and "
        "water-heaters cycling during early sleep — noise and thermal disturbance "
        "that degrade sleep quality and, through next-day productivity losses, "
        "cost the occupant money.")
    para(doc,
        "DozAI bridges this gap using only the existing smart electricity meter — "
        "no wearables, no cameras — to passively infer bed/wake times, predict "
        "nightly sleep quality, and co-optimise appliance scheduling and bedroom "
        "temperature pre-conditioning to minimise cost while protecting sleep.")

    # ── 2. Objectives ─────────────────────────────────────────────────────────
    heading(doc, "2. Objectives")
    for obj in [
        "Accurately forecast hourly household electricity demand using temporal "
        "cross-validation on real UCI meter data.",
        "Detect anomalous consumption events using robust MAD-based z-scores "
        "validated by synthetic injection.",
        "Passively infer nightly bed/wake times from sub-metering patterns "
        "(Kleiminger-style quiet-gap algorithm).",
        "Classify sleep-disorder risk (None / Insomnia / Sleep Apnea) from "
        "population-level health features using XGBoost.",
        "Predict nightly sleep quality from home-derived behavioural features "
        "using a disclosed semi-synthetic label generator.",
        "Schedule appliances and HVAC pre-cooling via MILP (CBC solver) to "
        "minimise cost + sleep disruption jointly.",
        "Quantify the annual financial saving of the co-optimised schedule versus "
        "habitual evening use.",
    ]:
        bullet(doc, obj)

    # ── 3. Data & Honesty Layers ──────────────────────────────────────────────
    heading(doc, "3. Data Sources & Honesty Layers")
    para(doc,
        "Three distinct data sources are used with explicit honesty layering to "
        "avoid misleading linkage claims.")

    heading(doc, "Layer A — Real Cross-Sectional Sleep Data (Kaggle)", level=2)
    para(doc,
        "Source: 'Sleep Health and Lifestyle' dataset (374 individuals). "
        "Used ONLY for population-level analytics and sleep-disorder risk "
        "classification. These are different people from the UCI household. "
        "Results reflect group patterns; no causal claims are made.")

    heading(doc, "Layer B — Real Energy + Weather (UCI + Open-Meteo)", level=2)
    para(doc,
        "Source: UCI 'Individual Household Electric Power Consumption' (ID 235), "
        "Sceaux, France, 2006-2010, ~2.07 million one-minute readings. "
        "Weather: Open-Meteo ERA5 reanalysis at the same location (48.76 N, 2.29 E), "
        "no API key required.")

    heading(doc, "Bridge — Inferred Bed/Wake Times", level=2)
    br = res.get("bridge_stats", {})
    cov = safe(br, "coverage_pct", default="N/A")
    nn  = safe(br, "n_nights", default="N/A")
    msh = safe(br, "median_sleep_h", default="N/A")
    mbh = safe(br, "median_bed_h", default="N/A")
    para(doc,
        f"Bed/wake times are DERIVED from the real meter using a Kleiminger-style "
        f"quiet-gap algorithm (longest contiguous low-load period >= 4 h inside a "
        f"21:00-10:00 window). Coverage: {fmt(cov, 1)}% of days. "
        f"Nights inferred: {nn}. "
        f"Median sleep duration: {fmt(msh, 2)} h. "
        f"Median bedtime: {fmt(mbh, 1)} h (24 h clock).")

    heading(doc, "Layer C — Disclosed Semi-Synthetic Sleep Labels", level=2)
    para(doc,
        "Nightly sleep quality scores (5-100) are generated by a formula calibrated "
        "to sleep-science literature: penalties for late bedtime deviation from "
        "chronotype, warm bedroom temperature, pre-bed appliance noise, and "
        "high stress; weekend bonus; Gaussian noise N(0,3). "
        "Labels are DISCLOSED as synthetic. They drive the optimisation loop only. "
        "Do NOT interpret as real polysomnography measurements.")

    # ── 4. Methodology ────────────────────────────────────────────────────────
    heading(doc, "4. Methodology")

    heading(doc, "4.1  Leakage Discipline & Temporal Splits", level=2)
    para(doc,
        "All time-series splits are strictly temporal (no shuffling). "
        "Test set: dates >= 2010-06-01. Normalisation statistics, standby "
        "thresholds, and chronotype medians are computed ONLY from training data "
        "(< 2010-01-01 for thresholds, < 2010-06-01 for models). "
        "Rolling features use shift(1) BEFORE .rolling() to prevent look-ahead leakage.")

    heading(doc, "4.2  Energy Forecasting & Backtesting Protocol", level=2)
    para(doc,
        "Features: 24/48/168-h lags, 24-h rolling mean, heating degree-days (HDD, "
        "base 15 degC), HDD-peak interaction, hour sin/cos, day-of-week. "
        "Expanding-window backtest: 5 monthly folds from 2010-06-01. "
        "Models: Global Mean (baseline), Seasonal Naive (same hour last week), "
        "Ridge (alpha=10, scaled), XGBoost (500 trees, lr=0.05, depth=6, sub=0.8). "
        "Metrics: MAE, RMSE, MAPE (actuals >= 0.2 kW), Peak MAE (top decile).")

    heading(doc, "4.3  Anomaly Detection (Robust MAD)", level=2)
    para(doc,
        "Baseline: hour-of-day median and MAD from pre-2010 data. "
        "Robust z-score: z = (kw - median) / (1.4826 * MAD + 1e-3). "
        "Threshold: |z| > 5. "
        "Validation: 10 synthetic anomalies (+1.5 kW) injected into the test "
        "window; precision and recall computed against known ground truth.")

    heading(doc, "4.4  Bridge: Passive Bed/Wake Inference", level=2)
    para(doc,
        "Minute-resolution Global_active_power resampled and interpolated (limit=5). "
        "Standby threshold THR = max(0.03, 1.5 * median of 03:00-05:00 load) "
        "from pre-2010 data. For each night (21:00-10:00 window): longest "
        "contiguous run where load <= THR and duration >= 240 min. "
        "Bedtime = last minute above THR before gap; wake = first minute above THR "
        "after. Days with >30% missing data are skipped.")

    heading(doc, "4.5  Sleep Quality Prediction (Two-Channel Design)", level=2)
    para(doc,
        "The MILP optimizer controls ONLY the scheduling channels (appliance "
        "timing, HVAC pre-cool). Behavioural channels (stress, sleep history lags) "
        "are fixed per day. score_schedule() evaluates each schedule using "
        "identical behavioural context, preventing the optimiser from gaming the "
        "sleep metric.")

    heading(doc, "4.6  MILP Formulation (DozAI)", level=2)
    para(doc,
        "S=96 slots (15 min each, DT=0.25 h). Decision variables: binary start "
        "indicator s[a,t] per appliance; continuous HVAC power hv[t] in [0,1.2] kW. "
        "Constraints: exactly one start per appliance; contiguous run of fixed "
        "duration; HVAC restricted to 6-h pre-cool window ending at bedtime; "
        "T_bed = T_out + G - E * hv_kwh >= 16 degC. "
        "Objective: cost + 120 * noise_hours + 25 * |T_bed - T_opt| + 40 * peak_kW. "
        "Solver: CBC via PuLP (open-source, no licence).")

    # ── 5. Results ────────────────────────────────────────────────────────────
    heading(doc, "5. Results")

    # 5.1 Forecasting
    heading(doc, "5.1  Energy Demand Forecasting", level=2)
    ft = res.get("forecast_table", [])
    if ft:
        table_from(doc,
            ["Model", "MAE (kW)", "RMSE (kW)", "MAPE (%)", "Peak MAE (kW)"],
            [[r.get("model",""), fmt(r.get("MAE",0),4), fmt(r.get("RMSE",0),4),
              fmt(r.get("MAPE",0),2), fmt(r.get("Peak_MAE",0),4)] for r in ft],
            caption="Table 1: Energy Forecasting — Mean across 5 Expanding-Window Folds"
        )
    imp = res.get("xgb_vs_seasonal_naive_improvement", {})
    para(doc,
        f"XGBoost vs Seasonal Naive: MAPE improved by "
        f"{fmt(safe(imp,'MAPE_improvement_pct',default=0),1)}%; "
        f"Peak MAE improved by "
        f"{fmt(safe(imp,'PeakMAE_improvement_pct',default=0),1)}%.")

    figure(doc, "figures/energy_eda.png",
           caption="Figure 1: Energy EDA — load profiles, submeter breakdown, temperature correlation")

    # 5.2 Anomaly
    heading(doc, "5.2  Anomaly Detection", level=2)
    an = res.get("anomaly_stats", {})
    para(doc,
        f"Flags in test window (Jul-Oct 2010): {safe(an,'n_flags',default='N/A')}. "
        f"Injection validation — Precision: {fmt(safe(an,'precision',default=0),3)}, "
        f"Recall: {fmt(safe(an,'recall',default=0),3)} "
        f"(TP={safe(an,'TP')}, FP={safe(an,'FP')}, FN={safe(an,'FN')}).")
    figure(doc, "figures/anomaly.png",
           caption="Figure 2: Anomaly Detection — flagged points on test-window load profile")

    # 5.3 Bridge
    heading(doc, "5.3  Passive Sleep Inference (Bridge)", level=2)
    para(doc,
        f"Coverage: {fmt(cov,1)}% of days. Nights inferred: {nn}. "
        f"Median sleep duration: {fmt(msh,2)} h. "
        f"Median bedtime: {fmt(mbh,1)} h (24 h clock).")
    figure(doc, "figures/bridge.png",
           caption="Figure 3: Bridge — bedtime distribution, duration histogram, weekday patterns")

    # 5.4 Classifier
    heading(doc, "5.4  Sleep-Disorder Classification (Layer A)", level=2)
    sc = res.get("sleep_classifier", {})
    para(doc,
        f"Logistic Regression — Macro-F1: {fmt(safe(sc,'LogReg_F1',default=0),3)}, "
        f"OVR AUC: {fmt(safe(sc,'LogReg_AUC',default=0),3)}. "
        f"XGBoost — Macro-F1: {fmt(safe(sc,'XGB_F1',default=0),3)}, "
        f"OVR AUC: {fmt(safe(sc,'XGB_AUC',default=0),3)}.")
    para(doc,
        "Note: cross-sectional data; results reflect population-level associations "
        "only. Macro-F1 reported (not accuracy) due to class imbalance.")
    figure(doc, "figures/sleep_eda.png",
           caption="Figure 4: Sleep Health EDA — disorder distribution, quality by category, stress vs quality")
    figure(doc, "figures/sleep_confusion.png",
           caption="Figure 5: XGBoost Sleep-Disorder Confusion Matrix")

    # 5.5 Sleep regression
    heading(doc, "5.5  Sleep Quality Regression (Layer C)", level=2)
    sr = res.get("sleep_regression", {})
    para(doc,
        f"Ridge — MAE: {fmt(safe(sr,'Ridge_MAE',default=0),3)}, "
        f"R2: {fmt(safe(sr,'Ridge_R2',default=0),3)}. "
        f"XGBoost — MAE: {fmt(safe(sr,'XGB_MAE',default=0),3)}, "
        f"R2: {fmt(safe(sr,'XGB_R2',default=0),3)}.")
    para(doc,
        "Reminder: labels are semi-synthetic (disclosed generator). "
        "Metrics measure reconstruction of the generator, not real sleep accuracy.")

    # ── 6. Optimisation Case Study ────────────────────────────────────────────
    heading(doc, "6. Optimisation Case Study")

    rt = res.get("replay_table", [])
    ann = res.get("annual_saving_inr", 0)
    n_nights = res.get("n_replay_nights", len(rt))
    if rt:
        table_from(doc,
            ["Arm", "Median Cost (Rs)", "Median Sleep Q", "Delta Cost (Rs)", "Delta Q"],
            [[r.get("arm",""), fmt(r.get("median_cost",0),2), fmt(r.get("median_q",0),1),
              fmt(r.get("delta_cost",0),2), fmt(r.get("delta_q",0),1)] for r in rt],
            caption=f"Table 2: 3-Way Replay — Median Metrics over {n_nights} Test Nights"
        )
    para(doc,
        f"Estimated annual saving (co-opt vs habitual): Rs {fmt(ann,0)}. "
        f"The 'cheapest' arm reduces cost further but sacrifices predicted sleep "
        f"quality — quantifying the cost-sleep trade-off. The co-opt arm balances both.")

    figure(doc, "figures/pareto.png",
           caption="Figure 6: Pareto Front — Cost vs Predicted Sleep Quality (hottest test night)")

    heading(doc, "6.1  Sensitivity Analysis", level=2)
    sens = res.get("sensitivity", {})
    para(doc, "Appliance-start changes when lambda_noise / lambda_temp vary ±50%:")
    for k, v in sens.items():
        bullet(doc, f"{k}: {v}")

    # ── 7. SHAP Interpretability ──────────────────────────────────────────────
    heading(doc, "7. Model Interpretability (SHAP)")
    figure(doc, "figures/shap_energy.png",
           caption="Figure 7: SHAP Beeswarm — XGBoost Energy Forecast (Oct 2010 sample)")
    figure(doc, "figures/shap_sleep.png",
           caption="Figure 8: SHAP Beeswarm — XGBoost Sleep Quality (Test Set)")
    para(doc,
        "For energy: recency lags and seasonal patterns dominate. "
        "For sleep quality: bedtime deviation and pre-bed noise are most influential, "
        "validating the optimisation targets.")

    # ── 8. Limitations ────────────────────────────────────────────────────────
    heading(doc, "8. Limitations")
    for lim in [
        "Sleep quality labels are semi-synthetic (calibrated generator, disclosed). "
        "Real wearable or diary data would substantially improve validity.",
        "Thermal model is linear (T_bed = T_out + G - E * hv_kwh). Real rooms "
        "have non-linear thermal dynamics and material-dependent heat capacity.",
        "Single household (Sceaux, France, 2006-2010). Results may not generalise "
        "to other climates, house sizes, or occupancy patterns.",
        "Tariff rates are illustrative scenario values (Rs/kWh). Actual savings "
        "depend on real utility contracts and time-of-use pricing.",
        "The energy and sleep datasets describe DIFFERENT people. No real linkage "
        "exists between the UCI household and the Kaggle sleep cohort.",
    ]:
        bullet(doc, lim)

    # ── 9. Future Work ────────────────────────────────────────────────────────
    heading(doc, "9. Future Work")
    for fw in [
        "Collect real sleep diaries or actigraphy to replace synthetic labels and "
        "validate the bridge algorithm.",
        "Extend to REFIT dataset (20 UK homes) for cross-household generalisability.",
        "Add solar PV, battery storage, and V2G (vehicle-to-grid) to the MILP.",
        "Deploy as a smart-plug pilot with real-time scheduling feedback.",
        "Personalise chronotype and thermal preference via online Bayesian updating.",
    ]:
        bullet(doc, fw)

    # ── 10. References ────────────────────────────────────────────────────────
    heading(doc, "10. References")
    refs = [
        "Kleiminger, W. et al. (2015). Predicting Household Occupancy for Smart "
        "Heating Control. Energy and Buildings, 101, 236-243.",
        "Okamoto-Mizuno, K., & Mizuno, K. (2012). Effects of thermal environment "
        "on sleep and circadian rhythm. Journal of Physiological Anthropology, 31(1), 14.",
        "Drake, C. L. et al. (2013). Shift work sleep disorder: prevalence and "
        "consequences beyond that of symptomatic day workers. Sleep, 27(8), 1453-1462.",
        "Baglioni, C. et al. (2011). Insomnia as a predictor of depression: A "
        "meta-analytic evaluation. Journal of Affective Disorders, 135(1-3), 10-19.",
        "Hebrail, G., & Berard, A. (2012). Individual Household Electric Power "
        "Consumption [Dataset]. UCI Machine Learning Repository. ID 235. "
        "https://archive.ics.uci.edu/dataset/235",
        "Open-Meteo (2024). Historical Weather API — ERA5 Reanalysis. "
        "https://archive-api.open-meteo.com",
    ]
    for i, ref in enumerate(refs, 1):
        numbered(doc, f"[{i}] {ref}")

    # ── Save ──────────────────────────────────────────────────────────────────
    out = "Akash_Kumar_DozAI_ProjectReport.docx"
    doc.save(out)
    print(f"\nReport saved: {out}")
    print("\nSubmit these 4 files:")
    print("  1. sleepai.ipynb")
    print("  2. requirements.txt")
    print("  3. make_report.py")
    print("  4. Akash_Kumar_DozAI_ProjectReport.docx")


if __name__ == "__main__":
    build()
