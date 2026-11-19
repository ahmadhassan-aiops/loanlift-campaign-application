"""Load the trained pipeline, score customers and explain the scores. No Streamlit here, so an API can use it too."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from loanlift.schema import FEATURES, Customer

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"


class LoanModel:
    """The saved scikit-learn pipeline (column selection + tuned XGBoost) and its metadata."""

    def __init__(self, model_dir: Path = MODEL_DIR):
        self.pipeline = joblib.load(model_dir / "loan_propensity_xgb.joblib")
        self.meta = json.loads((model_dir / "metadata.json").read_text(encoding="utf-8"))
        self.threshold: float = self.meta["threshold"]
        # Prospect: at or above the campaign threshold. Possible: from a third of it. Unlikely: below.
        self.tiers = (("Prospect", self.threshold), ("Possible", round(self.threshold / 3, 2)), ("Unlikely", 0.0))

    def predict_proba(self, rows: pd.DataFrame) -> np.ndarray:
        """Probability of taking a personal loan for rows that have the model's columns."""
        return self.pipeline.predict_proba(rows[FEATURES])[:, 1]

    def score(self, customer: Customer) -> float:
        return float(self.predict_proba(customer.to_frame())[0])

    def tier(self, p: float) -> str:
        return next(name for name, lower in self.tiers if p >= lower)

    def explain(self, rows: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
        """SHAP contribution of each feature (log-odds) and the bias, computed natively by XGBoost.

        For each row, bias + sum(contributions) is the model's log-odds of taking the loan.
        """
        encoded = self.pipeline.named_steps["prep"].transform(rows[FEATURES])
        booster = self.pipeline.named_steps["model"].get_booster()
        contribs = booster.predict(xgb.DMatrix(np.asarray(encoded, dtype=float), feature_names=FEATURES),
                                   pred_contribs=True)
        return pd.DataFrame(contribs[:, :-1], columns=FEATURES, index=rows.index), contribs[:, -1]


def to_prob(logit: float) -> float:
    return float(1 / (1 + np.exp(-logit)))
