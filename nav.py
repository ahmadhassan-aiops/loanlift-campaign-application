"""Page registry, shared by app.py and pages that link to other pages."""

import streamlit as st

from views import campaign, customer, method, performance, segments

CAMPAIGN = st.Page(campaign.render, title="Plan a campaign", icon=":material/campaign:", url_path="campaign",
                   default=True)
CUSTOMER = st.Page(customer.render, title="Check a customer", icon=":material/person_search:", url_path="customer")
SEGMENTS = st.Page(segments.render, title="Who buys", icon=":material/group_search:", url_path="segments")
PERFORMANCE = st.Page(performance.render, title="Model performance", icon=":material/fact_check:",
                      url_path="performance")
METHOD = st.Page(method.render, title="Data & method", icon=":material/dataset:", url_path="method")

PAGES = [CAMPAIGN, CUSTOMER, SEGMENTS, PERFORMANCE, METHOD]
