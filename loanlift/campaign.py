"""Campaign arithmetic: who to contact, what it costs and what it should bring in.

The model's probabilities are well calibrated (see the notebook), so the sum of the probabilities of the customers
contacted is the expected number of loans. When the real outcomes are known (the held-out customers), the actual
numbers are reported too.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Economics:
    cost_per_contact: float  # dollars per customer contacted (mailing, call time)
    value_per_loan: float    # net dollars the bank earns on one personal loan

    @property
    def break_even(self) -> float:
        """Contacting a customer pays off on average when their probability is at least cost / value."""
        return self.cost_per_contact / self.value_per_loan if self.value_per_loan else 1.0


def select(proba: np.ndarray, *, threshold: float | None = None, top_n: int | None = None) -> np.ndarray:
    """Boolean mask of the customers to contact: everyone at or above `threshold`, or the `top_n` highest scores."""
    proba = np.asarray(proba, dtype=float)
    if top_n is not None:
        mask = np.zeros(len(proba), dtype=bool)
        mask[np.argsort(-proba, kind="stable")[:max(0, min(top_n, len(proba)))]] = True
        return mask
    return proba >= (threshold if threshold is not None else 0.5)


def summary(proba: np.ndarray, contacted: np.ndarray, econ: Economics, outcome: np.ndarray | None = None) -> dict:
    """Contacts, expected (and actual) loans, uptake, cost and profit for a targeted campaign and for contacting all."""
    proba = np.asarray(proba, dtype=float)
    contacted = np.asarray(contacted, dtype=bool)
    n = int(contacted.sum())
    expected = float(proba[contacted].sum())
    out = {
        "customers": len(proba),
        "contacts": n,
        "share_contacted": n / len(proba) if len(proba) else 0.0,
        "expected_loans": expected,
        "expected_all": float(proba.sum()),
        "cost": n * econ.cost_per_contact,
        "profit": expected * econ.value_per_loan - n * econ.cost_per_contact,
        "profit_all": float(proba.sum()) * econ.value_per_loan - len(proba) * econ.cost_per_contact,
    }
    out["uptake"] = expected / n if n else 0.0
    out["share_of_loans"] = expected / out["expected_all"] if out["expected_all"] else 0.0
    if outcome is not None:
        outcome = np.asarray(outcome, dtype=int)
        actual = int(outcome[contacted].sum())
        out |= {
            "actual_loans": actual,
            "actual_all": int(outcome.sum()),
            "actual_uptake": actual / n if n else 0.0,
            "actual_share": actual / outcome.sum() if outcome.sum() else 0.0,
            "actual_profit": actual * econ.value_per_loan - n * econ.cost_per_contact,
            "actual_profit_all": int(outcome.sum()) * econ.value_per_loan - len(proba) * econ.cost_per_contact,
        }
    return out


def gains(proba: np.ndarray, outcome: np.ndarray | None = None, points: int = 101) -> pd.DataFrame:
    """Cumulative gains: share of customers contacted (best scores first) against share of loans reached.

    Uses the real outcomes when given, otherwise the expected loans (sum of probabilities).
    """
    proba = np.asarray(proba, dtype=float)
    order = np.argsort(-proba, kind="stable")
    hits = (np.asarray(outcome, dtype=float) if outcome is not None else proba)[order]
    cum = np.concatenate([[0.0], np.cumsum(hits)])
    total = cum[-1] or 1.0
    k = np.unique(np.round(np.linspace(0, len(proba), points)).astype(int))
    return pd.DataFrame({"contacted": k, "share_contacted": k / max(len(proba), 1), "share_loans": cum[k] / total,
                         "loans": cum[k]})
