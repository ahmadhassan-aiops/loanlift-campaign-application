"""Smoke test: every page renders without an exception, and the controls and example buttons work."""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["views/campaign.py", "views/customer.py", "views/segments.py", "views/performance.py", "views/method.py"]


def _page(path: str) -> AppTest:
    module = path.removesuffix(".py").replace("/", ".")
    script = f"""
import streamlit as st
from lib.ui import inject_css
import {module} as page
inject_css()
page.render()
"""
    return AppTest.from_string(script, default_timeout=60)


@pytest.mark.parametrize("path", PAGES)
def test_page_renders(path):
    at = _page(path).run()
    assert not at.exception, at.exception


@pytest.mark.parametrize("mode", ["Top N customers", "Most profitable"])
def test_campaign_modes(mode):
    at = _page("views/campaign.py").run()
    at.session_state["mode"] = mode
    at.run()
    assert not at.exception, at.exception


def test_example_button_loads_a_held_out_customer():
    at = _page("views/customer.py").run()
    at.button[1].click().run()  # "Likely buyer"
    assert not at.exception
    assert at.session_state["c_note"].startswith("Loaded held-out customer")
