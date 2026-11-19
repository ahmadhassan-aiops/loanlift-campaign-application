"""Plan a campaign: choose who to contact on a customer list, see what it costs and brings in, download the list."""

from __future__ import annotations

import io

import numpy as np
import pandas as pd
import streamlit as st

from loanlift import campaign
from loanlift.schema import EDUCATION, FEATURES, SHORT, validate_rows
from lib import charts, data, ui

TEMPLATE_ROWS = 5


def _money(x: float, sign: bool = False) -> str:
    """$1,234 / -$1,234, with an explicit + when `sign`."""
    prefix = "-" if x < 0 else ("+" if sign else "")
    return f"{prefix}${abs(x):,.0f}"


def _template() -> bytes:
    sample = data.test_set().head(TEMPLATE_ROWS)[FEATURES]
    sample.insert(0, "customer_id", [f"C{i:04d}" for i in range(1, TEMPLATE_ROWS + 1)])
    return sample.to_csv(index=False).encode()


def _source() -> tuple[pd.DataFrame | None, np.ndarray | None, str]:
    """The list to plan on: the held-out customers (outcome known) or an uploaded CSV. Returns (rows, outcome, name)."""
    choice = st.segmented_control(
        "Customer list", ["Last campaign's held-out customers", "Upload a list"], required=True,
        default="Last campaign's held-out customers", key="source",
    )
    if choice != "Upload a list":
        test = data.test_set()
        rows = test[FEATURES].copy()
        rows.insert(0, "customer_id", [f"T{int(i):04d}" for i in test["row_id"]])
        return rows, test["took_loan"].to_numpy(), "held-out"
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    up = c1.file_uploader("CSV with one row per customer (money in $000, flags as 0/1)", type="csv")
    c2.download_button("CSV template", _template(), "loanlift_template.csv", "text/csv",
                       icon=":material/download:", width="stretch")
    if up is None:
        ui.note("Upload a CSV with the columns <b>" + ", ".join(FEATURES) + "</b>. Any extra column, such as a "
                "customer ID, is kept in the download. Education is 1 (undergraduate), 2 (graduate) or "
                "3 (advanced/professional).")
        return None, None, "upload"
    raw = pd.read_csv(up)
    clean, errors = validate_rows(raw)
    if errors:
        st.warning("Some rows were left out:\n\n" + "\n".join(f"- {e}" for e in errors), icon=":material/rule:")
    if clean.empty:
        return None, None, "upload"
    extra = raw.loc[clean.index, [c for c in raw.columns if c not in FEATURES]]
    rows = pd.concat([extra, clean], axis=1)
    if "customer_id" not in rows.columns:
        rows.insert(0, "customer_id", [f"R{i + 1:04d}" for i in range(len(rows))])
    return rows.reset_index(drop=True), None, "upload"


def render() -> None:
    m = data.model()
    ref = data.reference()
    test = data.test_set()
    top10 = campaign.summary(test["proba"], campaign.select(test["proba"], top_n=len(test) // 10),
                             campaign.Economics(0, 1), test["took_loan"])
    ui.header(
        "LoanLift · personal loan campaign targeting",
        "Who should the next loan campaign reach?",
        f"Only <b>{m.meta['uptake_rate']:.1%}</b> of AllLife Bank's depositors took a personal loan in the last "
        "campaign. LoanLift scores every customer's chance of saying yes, so the campaign can <b>contact the few "
        "who will</b> and skip the many who will not. Pick a list, set a budget, download who to call.",
        chips=[("target", f"Top 10% of scores held {top10['actual_share']:.0%} of buyers"),
               ("verified", f"{ref['test']['Precision']:.0%} of contacted customers said yes"),
               ("savings", "Plan by threshold, budget or profit")],
    )

    rows, outcome, kind = _source()
    if rows is None:
        ui.footer()
        return
    proba = m.predict_proba(rows)
    known = outcome is not None

    # ---- Targeting controls ------------------------------------------------------------------------------
    with st.container(border=True):
        ui.panel_head(1, "Set the campaign", "Choose who to contact, and what a contact costs and a loan earns")
        a, b, c = st.columns([1.3, 1, 1])
        with a:
            mode = st.segmented_control("Contact customers", ["Above a score", "Top N customers", "Most profitable"],
                                        default="Above a score", required=True, key="mode")
        cost = b.number_input("Cost per contact ($)", min_value=0.0, max_value=1000.0, value=25.0, step=5.0,
                              help="Mailing, call time or a relationship manager's hour, per customer.")
        value = c.number_input("Net value of one loan ($)", min_value=1.0, max_value=100_000.0, value=600.0,
                               step=50.0, help="Interest income minus funding and default costs, over the loan.")
        econ = campaign.Economics(cost, value)
        if mode == "Above a score":
            t = st.slider("Contact customers whose chance of taking the loan is at least", 0.01, 0.95, m.threshold,
                          0.01, format="%.2f", key="t",
                          help=f"{m.threshold:.2f} is the model's recommended threshold (best F2 in cross-validation).")
            contacted = campaign.select(proba, threshold=t)
        elif mode == "Top N customers":
            n = st.slider("Number of customers to contact", 1, len(proba), min(len(proba), max(1, len(proba) // 10)),
                          key="n")
            contacted = campaign.select(proba, top_n=n)
            t = float(np.sort(proba)[::-1][n - 1])
        else:
            t = econ.break_even
            contacted = campaign.select(proba, threshold=t)
            st.html(f'<p class="sec-q">{ui.icon("calculate")}<span>A contact pays off on average when the customer\'s '
                    f'chance is at least cost ÷ value = <b>{t:.1%}</b>. Everyone above that is contacted.</span></p>')

    s = campaign.summary(proba, contacted, econ, outcome)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Customers to contact", f"{s['contacts']:,}", f"{s['share_contacted']:.0%} of {s['customers']:,}",
              delta_color="off", delta_arrow="off")
    if known:
        k2.metric("Buyers reached", f"{s['actual_loans']} of {s['actual_all']}",
                  f"{s['actual_share']:.0%} of all buyers", delta_color="off", delta_arrow="off")
        k3.metric("Said yes", f"{s['actual_uptake']:.0%}", f"vs {s['actual_all'] / s['customers']:.1%} contacting all",
                  delta_color="off", delta_arrow="off")
        k4.metric("Campaign profit", _money(s['actual_profit']),
                  f"{_money(s['actual_profit'] - s['actual_profit_all'], sign=True)} vs contacting all", delta_arrow="off")
    else:
        k2.metric("Expected loans", f"{s['expected_loans']:.0f}", f"{s['share_of_loans']:.0%} of the list's expected",
                  delta_color="off", delta_arrow="off")
        k3.metric("Expected to say yes", f"{s['uptake']:.0%}", f"vs {s['expected_all'] / s['customers']:.1%} contacting all",
                  delta_color="off", delta_arrow="off")
        k4.metric("Expected profit", _money(s['profit']), f"{_money(s['profit'] - s['profit_all'], sign=True)} vs contacting all",
                  delta_arrow="off")
    if known:
        ui.cap("These are the 1,000 customers the model never saw in training, with what they really did in the last "
               "campaign: the numbers are what this plan would have achieved. Profit uses your cost and value.")
    else:
        ui.cap("Expected loans add up each contacted customer's probability; the model's probabilities match real "
               "uptake closely (see Model performance).")

    # ---- Gains and profit ----------------------------------------------------------------------------------
    curve = campaign.gains(proba, outcome)
    reach = s["actual_share"] if known else s["share_of_loans"]
    with ui.spotlight_box("Contact a few, reach most of the buyers",
                          "Customers sorted by score, best first. The steeper the curve, the fewer contacts are "
                          "needed to reach the buyers; the dotted line is a campaign that picks customers at random."):
        ui.chart(charts.gains(curve, (s["share_contacted"], reach), actual=known), key="gains")
    order = np.argsort(-proba, kind="stable")
    counts = np.arange(0, len(proba) + 1)
    profits = np.concatenate([[0.0], np.cumsum(proba[order])]) * value - counts * cost
    best = int(np.argmax(profits))

    left, right = st.columns(2, gap="large")
    with left:
        ui.section("Profit by campaign size", "Expected profit as you contact more customers, best scores first")
        ui.chart(charts.profit(counts, profits, s["contacts"], best), key="profit")
    with right:
        ui.section("How the list scores", "Most customers are near 0%; buyers stand apart near 100%")
        ui.chart(charts.score_histogram(proba, t, outcome), key="hist")
    ui.insight(f"With a ${cost:,.0f} contact and a ${value:,.0f} loan, the most profitable campaign contacts the top "
               f"<b>{best:,}</b> customers (everyone with a chance of at least {econ.break_even:.1%}), for an expected "
               f"<b>{_money(profits[best])}</b>. Contacting the whole list would expect <b>{_money(s['profit_all'])}</b>.")

    # ---- The list ------------------------------------------------------------------------------------------
    with st.container(border=True):
        ui.panel_head(2, "Who to contact", "Ranked by chance of taking the loan; download the full scored list")
        contrib, _ = m.explain(rows)
        top_reason = contrib.idxmax(axis=1).map(SHORT)
        out = rows.assign(chance=proba, tier=[m.tier(p) for p in proba], contact=np.where(contacted, "Yes", "No"),
                          main_reason=np.where(proba >= m.threshold / 3, top_reason, ""))
        if known:
            out["took_loan_last_time"] = np.where(outcome == 1, "Yes", "No")
        out = out.sort_values("chance", ascending=False).reset_index(drop=True)
        show = out[out["contact"] == "Yes"] if st.toggle("Show only customers to contact", True, key="only") else out
        view = show.assign(Education=show["Education"].map(EDUCATION), chance=show["chance"] * 100)
        cols = ["customer_id", "chance", "tier", "main_reason", "Income", "CCAvg", "Family", "Education", "CD_Account"]
        if known:
            cols.append("took_loan_last_time")
        st.dataframe(
            view[cols], hide_index=True, height=380, width="stretch",
            column_config={
                "customer_id": "Customer",
                "chance": st.column_config.ProgressColumn("Chance of a yes", min_value=0, max_value=100, format="%.1f%%"),
                "tier": "Tier",
                "main_reason": st.column_config.TextColumn("Strongest reason", help="The feature that raises this "
                                                           "customer's score most (SHAP)."),
                "Income": st.column_config.NumberColumn("Income ($000)", format="%d"),
                "CCAvg": st.column_config.NumberColumn("Card spend/month ($000)", format="%.1f"),
                "Family": "Family",
                "Education": "Education",
                "CD_Account": st.column_config.CheckboxColumn("CD account"),
                "took_loan_last_time": "Took the loan (actual)",
            },
        )
        buf = io.StringIO()
        out.to_csv(buf, index=False)
        st.download_button(f"Download the scored list ({len(out):,} customers)", buf.getvalue().encode(),
                           "loanlift_scored_customers.csv", "text/csv", icon=":material/download:")
    ui.footer()
