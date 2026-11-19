"""Cached loaders: the model, the held-out customers, every customer and the reference statistics (built by train.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from loanlift.model import LoanModel

DATA = Path(__file__).resolve().parent.parent / "data"


@st.cache_resource(show_spinner="Loading the model...")
def model() -> LoanModel:
    return LoanModel()


@st.cache_data
def test_set() -> pd.DataFrame:
    """The 1,000 customers the model never saw in training, with their real response and predicted probability."""
    return pd.read_parquet(DATA / "test_scored.parquet")


@st.cache_data
def customers() -> pd.DataFrame:
    """All 5,000 customers and whether they took the loan (for the segment views, not for scoring)."""
    return pd.read_parquet(DATA / "customers.parquet")


@st.cache_data
def reference() -> dict:
    """Test metrics, medians for buyers and non-buyers, feature importance, calibration and model comparisons."""
    return json.loads((DATA / "reference.json").read_text(encoding="utf-8"))
