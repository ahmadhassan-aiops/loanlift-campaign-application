"""
Reproduce the model in model/ and the app's data/ files from the raw dataset.

The research (decision trees, 18 candidates, tuning, threshold choice) is in the notebook; this script replays
the final choice so the deployed artefact can be rebuilt and checked without a notebook:

    python train.py "path/to/Loan_Modelling.csv"

It writes model/loan_propensity_xgb.joblib, model/metadata.json, data/test_scored.parquet,
data/customers.parquet and data/reference.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score, average_precision_score, f1_score, fbeta_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from loanlift.model import LoanModel
from loanlift.schema import FEATURES

ROOT = Path(__file__).resolve().parent
PARAMS = {  # the notebook's tuned XGBoost (RandomizedSearchCV, 40 combinations, 5-fold PR-AUC)
    "n_estimators": 800, "learning_rate": 0.02, "max_depth": 6, "min_child_weight": 4, "subsample": 1.0,
    "colsample_bytree": 1.0, "gamma": 0, "reg_lambda": 10,
}

# Results from the notebook that are not recomputed here (they need the full model search)
TUNED = [  # 5-fold cross-validation on the training set
    {"Model": "Gradient boosting", "PR-AUC": 0.9842, "Std": 0.0062, "Log loss": 0.0384, "File (MB)": 0.7},
    {"Model": "Random forest", "PR-AUC": 0.9822, "Std": 0.0077, "Log loss": 0.0389, "File (MB)": 9.4},
    {"Model": "XGBoost (deployed)", "PR-AUC": 0.9797, "Std": 0.0064, "Log loss": 0.0393, "File (MB)": 1.1},
]
BASELINES = [  # best PR-AUC per algorithm, untuned, 5-fold cross-validation
    {"Model": "Random forest", "PR-AUC": 0.980}, {"Model": "XGBoost", "PR-AUC": 0.980},
    {"Model": "Gradient boosting", "PR-AUC": 0.979}, {"Model": "Bagging", "PR-AUC": 0.964},
    {"Model": "Decision tree (pruned)", "PR-AUC": 0.954}, {"Model": "AdaBoost", "PR-AUC": 0.894},
    {"Model": "Logistic regression", "PR-AUC": 0.849},
]

def load(csv: Path) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(csv)
    return df[FEATURES].copy(), df["Personal_Loan"].astype(int)


def build() -> Pipeline:
    prep = ColumnTransformer([("num", "passthrough", FEATURES)], verbose_feature_names_out=False)
    model = XGBClassifier(random_state=1, n_jobs=2, eval_metric="logloss", **PARAMS)
    return Pipeline([("prep", prep), ("model", model)])


def metrics(y, proba, t) -> dict:
    pred = (proba >= t).astype(int)
    return {
        "Accuracy": accuracy_score(y, pred), "Recall": recall_score(y, pred), "Precision": precision_score(y, pred),
        "F1": f1_score(y, pred), "F2": fbeta_score(y, pred, beta=2), "PR-AUC": average_precision_score(y, proba),
        "ROC-AUC": roc_auc_score(y, proba),
    }


def main(csv: Path) -> None:
    X, y = load(csv)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)

    pipe = build()
    oof = cross_val_predict(pipe, X_train, y_train, cv=cv, method="predict_proba", n_jobs=5)[:, 1]
    thresholds = np.round(np.arange(0.01, 0.951, 0.01), 2)
    threshold = float(thresholds[np.argmax([fbeta_score(y_train, oof >= t, beta=2) for t in thresholds])])

    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    test = {k: round(float(v), 4) for k, v in metrics(y_test, proba, threshold).items()}

    (ROOT / "model").mkdir(exist_ok=True)
    joblib.dump(pipe, ROOT / "model" / "loan_propensity_xgb.joblib")
    meta = {
        "model": "XGBoost",
        "threshold": threshold,
        "features": FEATURES,
        "params": PARAMS,
        "cv_pr_auc": round(float(average_precision_score(y_train, oof)), 4),
        "test": test,
        "test_rows": int(len(y_test)),
        "train_rows": int(len(y_train)),
        "uptake_rate": round(float(y.mean()), 4),
        "versions": {"scikit-learn": sklearn.__version__, "xgboost": xgb.__version__, "pandas": pd.__version__,
                     "numpy": np.__version__},
    }
    (ROOT / "model" / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # App data: the held-out customers with outcome and probability, and every customer for the segment views
    (ROOT / "data").mkdir(exist_ok=True)
    scored = X_test.copy()
    scored.insert(0, "row_id", np.arange(1, len(scored) + 1))
    scored["took_loan"] = y_test.to_numpy()
    scored["proba"] = proba
    scored.reset_index(drop=True).to_parquet(ROOT / "data" / "test_scored.parquet", index=False)
    X.assign(took_loan=y).to_parquet(ROOT / "data" / "customers.parquet", index=False)

    model = LoanModel(ROOT / "model")
    contrib, _ = model.explain(X_test)
    train = X_train.assign(took_loan=y_train)
    bins = pd.cut(oof, [0, 0.02, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0], include_lowest=True)
    calib = (pd.DataFrame({"p": oof, "y": y_train.to_numpy()}).groupby(bins, observed=True)
             .agg(predicted=("p", "mean"), observed=("y", "mean"), customers=("y", "size")))
    reference = {
        "test": test,
        "median_buyer": train[train.took_loan == 1][FEATURES].median().round(2).to_dict(),
        "median_nonbuyer": train[train.took_loan == 0][FEATURES].median().round(2).to_dict(),
        "importance": {k: round(float(v), 3) for k, v in contrib.abs().mean().sort_values(ascending=False).items()},
        "calibration": {k: [round(float(v), 4) for v in calib[k]] for k in calib.columns},
        "tuned": TUNED,
        "baselines": BASELINES,
    }
    (ROOT / "data" / "reference.json").write_text(json.dumps(reference, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "Loan_Modelling.csv")
