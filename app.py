"""
LoanLift: personal loan campaign targeting. Plan who to contact, check a customer, see which segments buy.
The trained pipeline ships in model/ (built by train.py); the inference code is in loanlift/.
"""

import streamlit as st

st.set_page_config(
    page_title="LoanLift | Ahmad Hassan",
    page_icon=":material/real_estate_agent:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from lib.ui import inject_css  # noqa: E402
from nav import PAGES  # noqa: E402

inject_css()
st.navigation(PAGES, position="top").run()
