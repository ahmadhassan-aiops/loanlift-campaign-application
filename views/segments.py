"""Who buys: the customer segments that took the loan in the last campaign, and a segment builder."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from loanlift.schema import EDUCATION
from lib import charts, data, ui

INCOME_BANDS = [0, 50, 75, 100, 125, 150, 250]
INCOME_LABELS = ["≤$50K", "$50-75K", "$75-100K", "$100-125K", "$125-150K", ">$150K"]
SPEND_BANDS = [-0.1, 1, 2, 3, 4, 11]
SPEND_LABELS = ["≤$1K", "$1-2K", "$2-3K", "$3-4K", ">$4K"]


def _rates(df: pd.DataFrame, by: str) -> tuple[list[str], list[float], list[int]]:
    g = df.groupby(by, observed=True)["took_loan"].agg(["mean", "size"])
    return [str(i) for i in g.index], g["mean"].tolist(), g["size"].tolist()


def render() -> None:
    df = data.customers()
    avg = df["took_loan"].mean()
    ui.header(
        "LoanLift · who buys",
        "Which customers take a personal loan?",
        f"In the last campaign <b>{df['took_loan'].sum()} of {len(df):,} customers</b> took the loan. They are not "
        "spread evenly: <b>income, card spending, education, family size and a CD account</b> pick them out, and "
        "the combinations matter more than any one fact.",
        page_icon="group_search",
        chips=[("database", f"{len(df):,} customers"), ("percent", f"{avg:.1%} took the loan")],
    )

    quiet = (df["Income"] <= 92.5) & (df["CCAvg"] <= 2.95)
    rich = df[df["Income"] > 100]
    a, b, c = st.columns(3)
    ui.finding(a, f"{quiet.mean():.0%}", f"of customers: {quiet.sum():,}, with {df.loc[quiet, 'took_loan'].sum()} buyers",
               "Most customers will not buy",
               "Income of $92.5K or less <b>and</b> card spending of $2.95K a month or less: <b>not one</b> of them "
               "took the loan. Leaving them out costs no sales.", card_icon="block")
    ui.finding(b, f"{rich[rich['Education'] >= 2]['took_loan'].mean():.0%}",
               "uptake: graduates and professionals earning over $100K",
               "Education decides among high earners",
               f"Undergraduates on the same incomes convert at only "
               f"<b>{rich[rich['Education'] == 1]['took_loan'].mean():.0%}</b>. Families of 3 or more earning over "
               f"$100K: <b>{rich[rich['Family'] >= 3]['took_loan'].mean():.0%}</b>.", card_icon="school")
    ui.finding(c, f"{df[df['CD_Account'] == 1]['took_loan'].mean():.0%}",
               f"uptake with a CD account (without: {df[df['CD_Account'] == 0]['took_loan'].mean():.0%})",
               "CD holders already trust the bank",
               "The strongest product signal. Online banking, securities and cards from other banks make "
               "almost no difference.", card_icon="savings")

    inc = pd.cut(df["Income"], INCOME_BANDS, labels=INCOME_LABELS)
    spend = pd.cut(df["CCAvg"], SPEND_BANDS, labels=SPEND_LABELS)
    rates = df.pivot_table(index=spend, columns=inc, values="took_loan", aggfunc="mean", observed=False)
    counts = df.pivot_table(index=spend, columns=inc, values="took_loan", aggfunc="size", observed=False)
    ui.spotlight("Income opens the door, card spending widens it",
                 "Share of customers who took the loan, by annual income (across) and monthly card spending (down). "
                 "Each cell shows the uptake and the number of customers.",
                 charts.uptake_heatmap(rates.iloc[::-1], counts.iloc[::-1], "Annual income", "Card spending per month",
                                       height=360), key="heat")
    ui.insight("Below <b>$75K</b> of income almost nobody buys, whatever they spend. From <b>$100K</b> up, uptake "
               "climbs fast. Card spending over <b>$3K a month</b> matters most in the middle: on $75K to $125K it "
               "lifts uptake to about 30%, from under 15% for most lower spenders. On low incomes it does little.")

    ui.section("Among high earners, who says yes?", "Customers earning over the income you choose, by education "
                                                    "and family size")
    floor = st.select_slider("Income over", options=[75, 100, 125, 150], value=100, format_func=lambda v: f"${v}K")
    high = df[df["Income"] > floor]
    edu = high["Education"].map(EDUCATION)
    r2 = high.pivot_table(index=edu, columns="Family", values="took_loan", aggfunc="mean").reindex(list(EDUCATION.values()))
    c2 = high.pivot_table(index=edu, columns="Family", values="took_loan", aggfunc="size").reindex(list(EDUCATION.values()))
    ui.chart(charts.uptake_heatmap(r2, c2, "Family size", "Education", height=280), key="edu_family")
    single_ug = (high["Education"] == 1) & (high["Family"] <= 2)
    ui.insight(f"Over ${floor}K, undergraduates in families of 1 or 2 take the loan at "
               f"<b>{high.loc[single_ug, 'took_loan'].mean():.0%}</b> ({single_ug.sum():,} customers). Everyone else "
               f"on these incomes, graduates and professionals or larger families, takes it at "
               f"<b>{high.loc[~single_ug, 'took_loan'].mean():.0%}</b>. A high income is necessary, not sufficient: "
               "the loan has to meet a need.")

    ui.section("Products and channels", "Uptake by each product the customer holds")
    labels, vals, ns = [], [], []
    for col, name in (("CD_Account", "CD account"), ("Securities_Account", "Securities account"),
                      ("Online", "Online banking"), ("CreditCard", "Other bank's card")):
        for flag, word in ((1, "with"), (0, "without")):
            part = df[df[col] == flag]
            labels.append(f"{name}<br>{word}")
            vals.append(part["took_loan"].mean())
            ns.append(len(part))
    ui.chart(charts.uptake_bars(labels, vals, ns, avg), key="products")

    ui.section("Build a segment", "Pick a target group and see how many buyers it holds")
    with st.container(border=True):
        a, b = st.columns(2)
        inc_rng = a.slider("Annual income ($000)", 0, 230, (100, 230), step=5)
        sp_rng = b.slider("Card spending per month ($000)", 0.0, 10.0, (0.0, 10.0), step=0.5)
        a, b, c = st.columns(3)
        edus = a.multiselect("Education", list(EDUCATION), default=list(EDUCATION), format_func=EDUCATION.get)
        fams = b.multiselect("Family size", [1, 2, 3, 4], default=[1, 2, 3, 4])
        cd = c.segmented_control("CD account", ["Any", "With", "Without"], default="Any", required=True)
        seg = df[df["Income"].between(*inc_rng) & df["CCAvg"].between(*sp_rng) & df["Education"].isin(edus)
                 & df["Family"].isin(fams)]
        if cd != "Any":
            seg = seg[seg["CD_Account"] == (1 if cd == "With" else 0)]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Customers in the segment", f"{len(seg):,}", f"{len(seg) / len(df):.0%} of all", delta_color="off",
                  delta_arrow="off")
        k2.metric("Took the loan", f"{seg['took_loan'].mean():.0%}" if len(seg) else "n/a",
                  f"vs {avg:.1%} overall", delta_color="off", delta_arrow="off")
        k3.metric("Buyers in the segment", f"{int(seg['took_loan'].sum())}", f"of {int(df['took_loan'].sum())}",
                  delta_color="off", delta_arrow="off")
        k4.metric("Share of all buyers", f"{seg['took_loan'].sum() / df['took_loan'].sum():.0%}", delta_arrow="off")
    ui.cap("Rules like these are easy to explain, but the model ranks customers inside and across segments; the "
           "Plan a campaign page reaches more buyers per contact than any single rule.")
    ui.footer()
