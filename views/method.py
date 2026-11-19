"""Data & method: the data, how the model was chosen, what was corrected, and the limits."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import data, ui
from lib.site import CODE_URL, NOTEBOOK_URL, PROJECT_URL


def render() -> None:
    m = data.model()
    ref = data.reference()
    ui.header(
        "LoanLift · data & method",
        "How LoanLift was built",
        "The data, the model search, the corrections made to the first version of the notebook, and what the model "
        "cannot do.",
        page_icon="dataset",
    )

    ui.section("The data")
    ui.md(
        "- **5,000 liability customers** (depositors) of AllLife Bank, a case-study bank, and whether each accepted "
        "the personal loan offered in the last campaign: **480 did (9.6%)**.\n"
        "- **Model inputs (10):** age, annual income, family size, monthly card spending, education, mortgage, and "
        "whether the customer has a securities account, a certificate of deposit (CD) account, online banking and a "
        "credit card from another bank. Money is in thousands of dollars.\n"
        "- **Not used:** `ID`; `Experience`, which is Age minus about 25 for every customer (correlation 0.99); and "
        "`ZIPCode`, whose regions all convert at 7.5% to 10.3%.\n"
        "- **Split:** 4,000 customers for training and 1,000 held out, stratified so both keep the 9.6% rate. "
        "Model choice, tuning and the threshold use 5-fold cross-validation on the training customers only."
    )

    ui.section("How the model was chosen")
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("**Step 1: 18 candidates, cross-validated PR-AUC** (best per algorithm)")
        st.dataframe(pd.DataFrame(ref["baselines"]), hide_index=True, width="stretch",
                     column_config={"PR-AUC": st.column_config.NumberColumn(format="%.3f")})
        ui.cap("Seven algorithms on the original data, with SMOTE oversampling inside each fold, and with class "
               "weights. Resampling raised recall at 0.5 but never improved the ranking.")
    with b:
        st.markdown("**Step 2: the three best, tuned** (40 combinations each)")
        st.dataframe(pd.DataFrame(ref["tuned"]), hide_index=True, width="stretch",
                     column_config={"PR-AUC": st.column_config.NumberColumn(format="%.4f"),
                                    "Std": st.column_config.NumberColumn("Fold std", format="%.4f"),
                                    "Log loss": st.column_config.NumberColumn(format="%.4f")})
        ui.cap("The three are statistically tied: the spread (0.0045) is smaller than each model's fold-to-fold "
               "standard deviation. XGBoost was deployed because it computes exact per-customer explanations "
               "natively, which the app shows for every score, in a 1 MB file.")
    ui.md(
        f"**Step 3: the threshold.** Out-of-fold predictions on the training customers; the threshold with the highest "
        f"F2 (recall weighted twice as much as precision) is **{m.threshold:.2f}**. The Plan a campaign page lets you "
        "replace it with a budget or a profit rule.\n\n"
        "**Step 4: one test.** The final model scored the 1,000 held-out customers once: recall "
        f"{ref['test']['Recall']:.1%}, precision {ref['test']['Precision']:.1%}, PR-AUC {ref['test']['PR-AUC']:.3f}."
    )

    ui.section("What was corrected in the first version")
    ui.recommendations([
        ("person_remove", "Outlier removal threw out the best prospects",
         "Customers outside the IQR fences of income and card spending were removed before splitting: 377 customers "
         "who convert at <b>40%</b>, holding <b>151 of the 480 buyers</b>. They are now kept."),
        ("science", "The test set chose the model",
         "The pruning strength was picked by recall on the test set, so the reported test score was optimistic. "
         "All choices now use cross-validation on the training data."),
        ("sync_alt", "Oversampling leaked into validation",
         "SMOTE ran once before cross-validation, so synthetic customers built from validation rows were trained "
         "on. Resampling now happens inside each fold, and the final model does not need it."),
        ("rule", "Findings read the wrong way",
         "The notebook said securities-account holders and mortgage holders buy less; both buy slightly more. "
         "\"Customers with credit cards\" counted CD accounts. Each finding is now recomputed."),
    ])

    ui.section("Limits")
    ui.md(
        "- **One campaign, one bank.** The model learned from a single campaign's 480 buyers. A different offer, "
        "rate or season can change who responds: re-train on each campaign's results.\n"
        "- **Marketing, not credit.** The score says who is likely to *want* a loan, not who should *get* one. "
        "Lending decisions need a separate credit assessment.\n"
        "- **Fair targeting.** Education and family size are strong predictors. Before use, check that the "
        "targeted groups and the offer meet the bank's fair-marketing rules.\n"
        "- **Explanations are associations.** SHAP shows what moves the model's score, not what causes a customer "
        "to borrow."
    )

    ui.section("Code and notebook")
    st.markdown(f"- [Notebook]({NOTEBOOK_URL}): the full analysis, corrections and model search\n"
                f"- [Project folder]({PROJECT_URL}) in the portfolio repository\n"
                f"- [App code]({CODE_URL}): Streamlit app, inference package, `train.py` and tests")
    ui.footer()
