"""How good is the model: held-out results, threshold trade-off, calibration and importance."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import confusion_matrix, precision_score, recall_score

from loanlift import campaign
from loanlift.schema import SHORT
from lib import charts, data, ui


@st.cache_data
def _curve(y: np.ndarray, p: np.ndarray) -> pd.DataFrame:
    ts = np.round(np.arange(0.01, 0.96, 0.01), 2)
    return pd.DataFrame({"threshold": ts,
                         "Recall": [recall_score(y, p >= t) for t in ts],
                         "Precision": [precision_score(y, p >= t, zero_division=0) for t in ts]})


def render() -> None:
    m = data.model()
    ref = data.reference()
    test = data.test_set()
    y, p = test["took_loan"].to_numpy(), test["proba"].to_numpy()
    ui.header(
        "LoanLift · model performance",
        "How well does LoanLift find buyers?",
        f"Every number here comes from <b>{len(test):,} customers the model never saw</b> during training or tuning, "
        f"scored once. {int(y.sum())} of them took the loan in the last campaign.",
        page_icon="fact_check",
    )
    s = ref["test"]
    top = campaign.summary(p, campaign.select(p, top_n=len(p) // 10), campaign.Economics(0, 1), y)
    a, b, c, d = st.columns(4)
    a.metric("Recall", f"{s['Recall']:.1%}", "share of buyers the model finds", delta_color="off", delta_arrow="off")
    b.metric("Precision", f"{s['Precision']:.1%}", "share of its prospects who said yes", delta_color="off",
             delta_arrow="off")
    c.metric("PR-AUC", f"{s['PR-AUC']:.3f}", f"random ranking scores {y.mean():.3f}", delta_color="off",
             delta_arrow="off")
    d.metric("Top 10% of scores", f"{top['actual_share']:.0%}", "of all buyers", delta_color="off", delta_arrow="off")

    with st.container(border=True):
        ui.section("Choose the threshold", "Lower it to reach more buyers, raise it to waste fewer contacts")
        t = st.slider("Contact customers at or above", 0.01, 0.95, m.threshold, 0.01, key="perf_t")
        left, right = st.columns([1.25, 1], gap="large")
        left.plotly_chart(charts.tradeoff(_curve(y, p), t), theme=None, config=charts.CONFIG, key="tradeoff")
        tn, fp, fn, tp = confusion_matrix(y, p >= t).ravel()
        right.plotly_chart(charts.confusion(tn, fp, fn, tp), theme=None, config=charts.CONFIG, key="cm")
        ui.insight(f"At {t:.2f} the campaign contacts <b>{tp + fp}</b> of {len(y):,} customers and reaches <b>{tp} of "
                   f"{tp + fn} buyers</b>; {fp} contacts say no. The recommended {m.threshold:.2f} was chosen in "
                   "cross-validation (highest F2, which weighs a missed buyer twice as much as a wasted contact), "
                   "before the test set was opened.")

    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        ui.section("Can the percentages be trusted?", "Predicted against actual uptake, out of fold")
        cal = ref["calibration"]
        ui.chart(charts.calibration(cal["predicted"], cal["observed"], cal["customers"]), key="cal")
        ui.cap(f"{int(cal['customers'][0]):,} of 4,000 training customers score under 2% and none of them took the loan; "
               f"{int(cal['customers'][-1]):,} score over 90% and {cal['observed'][-1]:.0%} of them did. The thin middle "
               "(124 customers between 10% and 50%) is within about 4 to 9 points.")
    with right, st.container(border=True):
        ui.section("What the model relies on", "Average impact of each feature on the score")
        imp = ref["importance"]
        ui.chart(charts.importance([SHORT[k] for k in imp], list(imp.values())), key="imp")
        ui.cap("Income dominates; card spending, education and family size follow. Age and the product flags "
               "other than a CD account barely matter.")

    ui.footer()
