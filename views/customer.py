"""Check one customer: a form on the left; the chance of a yes, the reasons and how to pitch on the right."""

from __future__ import annotations

import streamlit as st
from pydantic import ValidationError

from loanlift import offers
from loanlift.model import to_prob
from loanlift.schema import EDUCATION, LABELS, Customer
from lib import data, ui

DEFAULTS = {  # the typical (median / most common) customer in the data
    "Age": 45, "Income": 64.0, "Family": 2, "CCAvg": 1.5, "Education": 1, "Mortgage": 0.0,
    "Securities_Account": 0, "CD_Account": 0, "Online": 1, "CreditCard": 0,
}
KEY = "c_"  # widget keys are KEY + column name
FLAGS = ["CD_Account", "Securities_Account", "Online", "CreditCard"]


def _load(values: dict) -> None:
    for col, v in values.items():
        if col in DEFAULTS:
            st.session_state[KEY + col] = bool(v) if col in FLAGS else type(DEFAULTS[col])(v)


def _load_example(kind: str) -> None:
    test = data.test_set()
    if kind == "buyer":
        pool = test[(test["took_loan"] == 1) & (test["proba"] >= 0.9)]
    elif kind == "borderline":
        pool = test[test["proba"].between(0.15, 0.6)]
    else:
        pool = test
    row = pool.sample(1).iloc[0].to_dict()
    _load(row)
    st.session_state["c_note"] = (
        f"Loaded held-out customer #{int(row['row_id'])}, who in the last campaign "
        f"<b>{'took the loan' if row['took_loan'] else 'did not take the loan'}</b>. The model never saw them in training."
    )


def _init() -> None:
    if KEY + "Age" not in st.session_state:
        _load(DEFAULTS)
        st.session_state["c_note"] = "Showing a typical customer (the median of every field). Change anything."


def _form() -> dict:
    v = {}
    k = lambda c: {"key": KEY + c, "label": LABELS[c]}  # noqa: E731
    with st.container(border=True):
        st.markdown("**Who they are**")
        a, b = st.columns(2)
        v["Age"] = a.number_input(min_value=18, max_value=100, step=1, **k("Age"))
        v["Family"] = b.segmented_control(options=[1, 2, 3, 4], required=True, **k("Family"))
        v["Education"] = st.segmented_control(options=list(EDUCATION), format_func=EDUCATION.get, required=True,
                                              **k("Education"))
    with st.container(border=True):
        st.markdown("**Money**, in thousands of dollars")
        v["Income"] = st.slider(min_value=0.0, max_value=250.0, step=1.0, format="$%.0fK", **k("Income"))
        v["CCAvg"] = st.slider(min_value=0.0, max_value=10.0, step=0.1, format="$%.1fK", **k("CCAvg"))
        v["Mortgage"] = st.number_input(min_value=0.0, max_value=1000.0, step=10.0, format="%.0f", **k("Mortgage"))
    with st.container(border=True):
        st.markdown("**Products and channels**")
        a, b = st.columns(2)
        for i, col in enumerate(FLAGS):
            v[col] = int((a if i % 2 == 0 else b).toggle(**k(col)))
    return v


def _value(col: str, x) -> str:
    if col == "Income":
        return f"${x:,.0f}K"
    if col == "CCAvg":
        return f"${x:.1f}K/month"
    if col == "Mortgage":
        return f"${x:,.0f}K" if x else "none"
    if col == "Education":
        return EDUCATION[int(x)]
    if col in FLAGS:
        return "yes" if x else "no"
    return f"{x:.0f}"


def _similar(c: Customer) -> tuple[int, int, str]:
    """Customers in the data with a similar profile: same income band, education group and family group."""
    df = data.customers()
    lo, hi = max(0, c.Income - 15), c.Income + 15
    same = df[df["Income"].between(lo, hi)
              & ((df["Education"] >= 2) == (c.Education >= 2))
              & ((df["Family"] >= 3) == (c.Family >= 3))]
    desc = (f"income ${lo:.0f}K to ${hi:.0f}K, {'graduate or higher' if c.Education >= 2 else 'undergraduate'}, "
            f"family of {'3 or more' if c.Family >= 3 else '1 or 2'}")
    return int(same["took_loan"].sum()), len(same), desc


def render() -> None:
    _init()
    m = data.model()
    ref = data.reference()
    ui.header(
        "LoanLift · check a customer",
        "Will this customer take a personal loan?",
        "Enter a depositor's profile. LoanLift gives the <b>chance they accept a loan offer</b>, shows <b>which facts "
        "drive it</b>, and suggests <b>how to approach them</b>. Everything updates as you type.",
        page_icon="person_search",
        chips=[("target", f"Finds {ref['test']['Recall']:.0%} of buyers"),
               ("verified", f"{ref['test']['Precision']:.0%} of its prospects say yes"),
               ("bolt", "Live: updates as you type")],
    )
    b1, b2, b3, b4 = st.columns(4)
    b1.button("Typical customer", icon=":material/person:", on_click=_load, args=(DEFAULTS,), width="stretch")
    b2.button("Likely buyer", icon=":material/thumb_up:", on_click=_load_example, args=("buyer",), width="stretch")
    b3.button("Borderline case", icon=":material/balance:", on_click=_load_example, args=("borderline",),
              width="stretch")
    b4.button("Random held-out customer", icon=":material/casino:", on_click=_load_example, args=("random",),
              width="stretch")
    if note := st.session_state.get("c_note"):
        st.html(f'<p class="sec-q">{ui.icon("info")}<span>{note}</span></p>')

    left, right = st.columns([1, 1.1], gap="large")
    with left:
        values = _form()
    try:
        customer = Customer(**values)
    except ValidationError as exc:
        right.error(exc.errors()[0]["msg"].removeprefix("Value error, "), icon=":material/error:")
        return
    row = customer.to_frame()
    p = float(m.predict_proba(row)[0])
    tier = m.tier(p)
    contrib, bias = m.explain(row)
    contrib = contrib.iloc[0]
    t, low = m.threshold, m.tiers[1][1]
    buyers, similar, desc = _similar(customer)

    with right:
        with st.container(border=True):
            ui.panel_head(1, "Chance of a yes", f"Out of 100 customers like this one · the campaign contacts from "
                                                f"{t:.0%}")
            share = ("Almost all" if p > 0.99 else "Fewer than 1" if p < 0.01 else f"About {round(p * 100)}")
            ui.people(p, tier, f"<b>{share} of 100</b> customers with this profile would take the loan.")
            if tier == "Prospect":
                text = "<b>Contact this customer.</b> They are in the group the campaign should reach."
            elif tier == "Possible":
                text = "<b>A possible buyer.</b> Worth a low-cost contact, not a call."
            else:
                text = "<b>Unlikely to take a loan now.</b> Leave them out of this campaign."
            facts = [("groups", f"Similar customers: {buyers} of {similar} took the loan" if similar else
                      "No similar customers in the data")]
            ui.verdict(tier, text, [("Unlikely", f"under {low:.0%}"), ("Possible", f"{low:.0%} to {t:.0%}"),
                                    ("Prospect", f"{t:.0%} or more")], facts)
            ui.cap(f"Similar customers: {desc}, from all 5,000 customers in the last campaign.")

        with st.container(border=True):
            ui.panel_head(2, "Why", "The facts that move this customer's chance most, against a typical buyer")
            top = contrib.reindex(contrib.abs().sort_values(ascending=False).index)[:5]
            buyer = ref["median_buyer"]
            ui.drivers([{"name": LABELS[c], "value": _value(c, row.iloc[0][c]),
                         "typical": _value(c, buyer[c]) if c not in FLAGS else "", "shap": float(v)}
                        for c, v in top.items()])
            ui.cap(f"Bar length is the feature's SHAP contribution relative to the strongest. From the model's "
                   f"baseline ({to_prob(float(bias[0])):.0%}) the contributions add up to this score.")

    with st.container(border=True):
        ui.panel_head(3, "How to pitch", "The contact channel follows the score; the angles follow the profile")
        ui.pitch_channel(tier, *offers.channel(p, t, bool(customer.Online)))
        if tier != "Unlikely":
            items = [(i, title, "", body) for i, title, body in offers.angles(customer.model_dump())]
            ui.action_cards(items, tag="Angle")
    ui.footer()
