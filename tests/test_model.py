"""Checks that the shipped model, its metadata, the inference code and the campaign maths agree. Run: pytest -q"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score, precision_score, recall_score

from loanlift import campaign, offers
from loanlift.model import LoanModel
from loanlift.schema import FEATURES, Customer, validate_rows
from lib.data import DATA

TYPICAL = dict(Age=45, Income=64, Family=2, CCAvg=1.5, Education=1, Mortgage=0, Securities_Account=0,
               CD_Account=0, Online=1, CreditCard=0)
PROSPECT = dict(Age=40, Income=160, Family=4, CCAvg=4.5, Education=3, Mortgage=0, Securities_Account=0,
                CD_Account=1, Online=1, CreditCard=0)


@pytest.fixture(scope="module")
def model() -> LoanModel:
    return LoanModel()


@pytest.fixture(scope="module")
def test_set() -> pd.DataFrame:
    return pd.read_parquet(DATA / "test_scored.parquet")


def test_metadata_is_sane(model):
    assert 0 < model.threshold < 1
    assert model.meta["features"] == FEATURES
    assert model.meta["test"]["Recall"] > 0.9 and model.meta["test"]["Precision"] > 0.85


def test_shipped_predictions_reproduce(model, test_set):
    assert np.allclose(model.predict_proba(test_set), test_set["proba"], atol=1e-6)


def test_metadata_matches_the_test_set(model, test_set):
    y, p = test_set["took_loan"], test_set["proba"]
    t = model.threshold
    assert recall_score(y, p >= t) == pytest.approx(model.meta["test"]["Recall"], abs=1e-4)
    assert precision_score(y, p >= t) == pytest.approx(model.meta["test"]["Precision"], abs=1e-4)
    assert average_precision_score(y, p) == pytest.approx(model.meta["test"]["PR-AUC"], abs=1e-4)


def test_shap_adds_up_to_the_prediction(model, test_set):
    rows = test_set.head(50)
    contrib, bias = model.explain(rows)
    logit = contrib.sum(axis=1).to_numpy() + bias
    assert np.allclose(1 / (1 + np.exp(-logit)), model.predict_proba(rows), atol=1e-5)


def test_profiles_score_sensibly(model):
    low, high = model.score(Customer(**TYPICAL)), model.score(Customer(**PROSPECT))
    assert low < 0.02 < 0.9 < high
    assert model.tier(low) == "Unlikely" and model.tier(high) == "Prospect"


def test_schema_rejects_bad_values():
    with pytest.raises(ValueError):
        Customer(**{**TYPICAL, "Education": 4})
    with pytest.raises(ValueError):
        Customer(**{**TYPICAL, "Income": -5})


def test_validate_rows_reports_and_skips_bad_rows():
    raw = pd.DataFrame([TYPICAL, {**TYPICAL, "Age": 5}, PROSPECT]).assign(customer_id=["a", "b", "c"])
    clean, errors = validate_rows(raw)
    assert len(clean) == 2 and list(clean.columns) == FEATURES
    assert errors == ["Row 2: Age: Input should be greater than or equal to 18"]
    _, missing = validate_rows(raw.drop(columns=["CCAvg"]))
    assert missing == ["Missing column(s): CCAvg"]


def test_campaign_selection_and_summary():
    p = np.array([0.9, 0.1, 0.5, 0.02])
    assert campaign.select(p, threshold=0.3).tolist() == [True, False, True, False]
    assert campaign.select(p, top_n=1).tolist() == [True, False, False, False]
    econ = campaign.Economics(cost_per_contact=10, value_per_loan=100)
    assert econ.break_even == pytest.approx(0.1)
    s = campaign.summary(p, campaign.select(p, threshold=0.3), econ, outcome=np.array([1, 0, 1, 0]))
    assert s["contacts"] == 2 and s["expected_loans"] == pytest.approx(1.4)
    assert s["profit"] == pytest.approx(1.4 * 100 - 20) and s["actual_loans"] == 2 and s["actual_share"] == 1


def test_gains_curve_ends_at_all_buyers(test_set):
    g = campaign.gains(test_set["proba"], test_set["took_loan"])
    assert g["share_loans"].iloc[0] == 0 and g["share_loans"].iloc[-1] == pytest.approx(1)
    assert g["share_loans"].is_monotonic_increasing


def test_offers_follow_the_profile(model):
    assert offers.channel(0.95, model.threshold, True)[1].startswith("Personal call")
    assert offers.channel(0.01, model.threshold, True)[1] == "Leave out of this campaign"
    titles = [t for _, t, _ in offers.angles(PROSPECT)]
    assert "Consolidate card spending" in titles and "Family plans" in titles
    assert [t for _, t, _ in offers.angles(TYPICAL)] == ["General-purpose personal loan"]
