"""LoanLift's page furniture: a banker's ledger. Ruled ledger sheets with a red double margin, a letterhead with
rubber-stamp chips, serif folios, ledger notes, the campaign ledger (spend, income, net with a double underline), the
100-customer stamp sheet, driver rows and pitch cards."""

from __future__ import annotations

import html

import streamlit as st

from lib import theme
from lib.charts import CONFIG
from lib.site import CODE_URL, DATA_CREDIT, LEARN_URL, NOTEBOOK_URL

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,500;0,600;0,700;0,800;1,500;1,600&family=Public+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
:root { --ink:#1f2a24; --ink-2:#4a554f; --muted:#64706a; --line:#d6dccf; --surface:#fdfdf7; --paper:#fffef8;
        --accent:__ACCENT__; --accent-ink:__INK__; --accent-soft:__SOFT__; --accent-tint:__TINT__;
        --rule:#e2ecdf; --margin:#d9534f; --warn:#8a5a00; --warn-soft:#fdf6e7;
        --serif:'Spectral', Georgia, serif; --sans:'Public Sans', 'Segoe UI', sans-serif; --mono:'DM Mono', Consolas, monospace; }
html, body, [data-testid="stAppViewContainer"] { font-family: var(--sans); color: var(--ink); }
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #ece7d6; }
header[data-testid="stHeader"] { background: var(--paper); border-bottom: 4px double var(--accent); }
.block-container { padding-top: 4.6rem; max-width: 1180px; }
h1, h2, h3 { color: var(--ink); font-family: var(--serif); }
.msr { font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal; line-height: 1;
       letter-spacing: normal; text-transform: none; white-space: nowrap; direction: ltr; display: inline-block;
       -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased; }

/* Ledger sheets: ruled green lines and a red double margin rule */
[data-testid="stVerticalBlock"][data-test-scroll-behavior] { border: 1px solid #cfd6c4 !important; border-radius: 3px !important;
    background: linear-gradient(90deg, transparent 1.55rem, var(--margin) 1.55rem, var(--margin) calc(1.55rem + 1px),
                transparent calc(1.55rem + 1px), transparent calc(1.55rem + 4px), var(--margin) calc(1.55rem + 4px),
                var(--margin) calc(1.55rem + 5px), transparent calc(1.55rem + 5px)),
                var(--paper) !important;
    padding-left: 2.5rem !important; box-shadow: 0 8px 20px -14px rgba(31,42,36,.35); }

/* Ruled writing: prose on a sheet sits on its own ruled lines. The rule spacing equals the line height, so every line of
   text falls between two rules whatever the content above it (a sheet-wide ruling cannot line up with mixed content). */
:root { --lh: 1.75rem; }
.ruled, [data-test-scroll-behavior] [data-testid="stCaptionContainer"] p, .insight > div:last-child, .note > div:last-child,
[data-test-scroll-behavior] .verdict-text, [data-test-scroll-behavior] .card-text, [data-test-scroll-behavior] .spot-text,
[data-test-scroll-behavior] [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] > p,
[data-test-scroll-behavior] [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] li {
    line-height: var(--lh) !important;
    background: repeating-linear-gradient(180deg, transparent 0, transparent calc(var(--lh) - 1px), var(--rule) calc(var(--lh) - 1px),
                var(--rule) var(--lh)); }
[data-test-scroll-behavior] [data-testid="stCaptionContainer"] p { font-style: italic; color: var(--ink-2); }
.insight, .note { align-items: flex-start; }
.callout-icon { line-height: var(--lh); padding-top: 0; }

/* Letterhead */
.hero { background: var(--paper); border: 1px solid #cfd6c4; border-top: 5px solid var(--accent); padding: 1.1rem 1.4rem;
        margin: 0 0 1.4rem; box-shadow: 0 8px 20px -14px rgba(31,42,36,.35); }
.hero-icon { display: none; }
.kicker { font-family: var(--mono); font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--accent-ink); margin: 0 0 .35rem; }
.hero h1 { font-family: var(--serif); font-size: 2.3rem; line-height: 1.1; font-weight: 800; margin: 0 0 .45rem; padding: 0; }
.lead { font-size: 1.02rem; color: var(--ink-2); max-width: 820px; line-height: 1.62; margin: 0; }
.lead b { color: var(--ink); }
.chips { display: flex; flex-wrap: wrap; gap: .6rem; margin: .9rem 0 0; }
.chip { display: inline-flex; align-items: center; gap: .3rem; font-family: var(--mono); font-size: .72rem; letter-spacing: .05em;
        text-transform: uppercase; color: var(--accent-ink); border: 2px solid var(--accent); outline: 1px solid var(--accent);
        outline-offset: 2px; padding: .15rem .55rem; transform: rotate(-.6deg); background: transparent; }
.chip:nth-child(2) { transform: rotate(.5deg); } .chip:nth-child(3) { transform: rotate(-.3deg); }
.chip .msr { font-size: 15px; }

/* Section headings: serif with a double rule */
[data-testid="stHeading"] h3 { font-family: var(--serif); font-weight: 700; border-bottom: 3px double var(--accent); padding-bottom: .15rem; margin-top: .4rem; }
.sec-q { display: flex; align-items: flex-start; gap: .4rem; color: var(--ink-2); font-size: .9rem; line-height: 1.45; font-style: italic;
         margin: -.2rem 0 .7rem; }
.sec-q .msr { font-size: 18px; color: var(--accent-ink); font-style: normal; }

/* Metrics as ledger cells */
[data-testid="stMetric"] { background: var(--paper); border: 1px solid #cfd6c4; border-top: 3px double var(--accent); padding: .55rem .8rem !important; }
[data-testid="stMetricValue"] { font-family: var(--mono); font-weight: 500; color: var(--ink); }
[data-testid="stMetricLabel"] p { font-family: var(--mono); font-size: .72rem !important; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }

/* Callouts: ledger notes and caveats */
.insight, .note { display: flex; gap: .7rem; align-items: flex-start; padding: .7rem 1rem; color: var(--ink); font-size: .97rem;
                  line-height: 1.6; margin: .3rem 0 1.4rem; background: var(--paper); }
.insight { border: 1px solid var(--accent-tint); border-left: 4px solid var(--accent); }
.insight b { color: var(--accent-ink); }
.note { border: 1px solid #ecd9a8; border-left: 4px solid #b77800; background: #fffaf0; font-size: .94rem; }
.callout-icon { flex: none; font-family: var(--serif); font-style: italic; font-weight: 600; font-size: .9rem; color: var(--accent-ink);
                padding-top: .05rem; white-space: nowrap; }
.callout-icon .msr { display: none; }
.insight .callout-icon::before { content: "Ledger note"; }
.note .callout-icon::before { content: "Caveat"; color: #8a5a00; }

/* Finding cards and spotlight */
.f-head { display: none; }
.big { font-family: var(--mono); font-size: 2rem; font-weight: 500; color: var(--accent-ink); line-height: 1.1; margin: .2rem 0 0; }
.big-label { color: var(--muted); font-size: .84rem; margin: .15rem 0 .6rem; padding-bottom: .6rem; border-bottom: 3px double var(--line); }
.card-title { font-family: var(--serif); font-weight: 700; font-size: 1.12rem; margin: 0 0 .3rem; }
.card-text { color: var(--ink-2); font-size: .94rem; line-height: 1.55; margin: 0 0 .5rem; }
.card-text b { color: var(--ink); }
.spot { display: flex; align-items: baseline; flex-wrap: wrap; gap: .4rem .7rem; margin: 0 0 .1rem; }
.spot-tag { font-family: var(--mono); font-size: .66rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent-ink);
            border: 1.5px solid var(--accent); padding: .1rem .45rem; flex: none; }
.spot-title { font-family: var(--serif); font-size: 1.35rem; font-weight: 700; margin: 0; }
.spot-text { color: var(--ink-2); font-size: .94rem; line-height: 1.55; margin: .2rem 0 .3rem; max-width: 860px; font-style: italic; }

/* Recommendations and method */
.recs { display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: .9rem; margin: .25rem 0 .9rem; }
.rec { background: var(--paper); border: 1px solid var(--line); border-top: 3px double var(--accent); padding: .9rem 1rem; }
.rec-head { display: flex; align-items: center; gap: .6rem; margin-bottom: .4rem; }
.rec-num { font-family: var(--serif); font-style: italic; font-weight: 700; color: var(--accent-ink); }
.rec-icon { color: var(--accent-ink); font-size: 22px; margin-left: auto; }
.rec-title { font-weight: 700; margin: 0; } .rec-text { color: var(--ink-2); font-size: .93rem; line-height: 1.55; margin: 0; }
.method { display: flex; gap: .9rem; } .method-icon { display: none; } .method p { color: var(--ink-2); margin: 0; }
[data-testid="stMarkdownContainer"] ol li::marker { color: var(--accent-ink); font-family: var(--serif); font-weight: 700; }
[data-testid="stMarkdownContainer"] ul li::marker { color: var(--accent); }

/* Result panels */
.band { display: inline-flex; align-items: center; gap: .3rem; font-family: var(--mono); font-weight: 500; font-size: .78rem; text-transform: uppercase;
        letter-spacing: .1em; color: var(--band-ink); border: 2px solid var(--band); outline: 1px solid var(--band); outline-offset: 2px;
        padding: .2rem .6rem; transform: rotate(-1.5deg); background: transparent; }
.band .msr { font-size: 17px; }
.derived { display: flex; gap: .5rem; flex-wrap: wrap; margin: .2rem 0 0; }
.panel-head { display: flex; gap: .7rem; align-items: baseline; margin: 0 0 .5rem; border-bottom: 3px double var(--accent); padding-bottom: .3rem; }
.panel-num { flex: none; font-family: var(--serif); font-style: italic; font-weight: 600; font-size: .92rem; color: var(--accent-ink); }
.panel-num::before { content: "Folio "; }
.panel-title { font-family: var(--serif); font-weight: 700; font-size: 1.3rem; margin: 0; line-height: 1.2; }
.panel-sub { color: var(--muted); font-size: .84rem; margin: .1rem 0 0; line-height: 1.35; font-style: italic; }
.score-top { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; margin: .4rem 0 .5rem; }
.verdict-text { color: var(--ink-2); font-size: .96rem; line-height: 1.55; margin: .1rem 0 .7rem; }
.verdict-text b { color: var(--ink); }
.ladder { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border: 1px solid var(--line); margin: 0 0 .7rem; background: var(--paper); }
.rung { padding: .4rem .6rem; border-right: 1px solid var(--line); opacity: .55; }
.rung:last-child { border-right: none; }
.rung.on { opacity: 1; background: var(--band-soft); box-shadow: inset 0 -3px 0 var(--band); }
.rung-name { display: flex; align-items: center; gap: .3rem; font-weight: 700; font-size: .82rem; color: var(--band-ink); margin: 0; }
.rung-name .msr { font-size: 16px; }
.rung-range { font-family: var(--mono); font-size: .72rem; color: var(--ink-2); margin: .1rem 0 0; }
.facts { display: flex; flex-wrap: wrap; gap: .4rem; }
.facts .chip { transform: none; outline: none; border-width: 1px; text-transform: none; letter-spacing: 0; font-size: .78rem; }

.drv-legend { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: .75rem; font-family: var(--mono); font-size: .66rem;
              letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: .3rem 0 .1rem; }
.drv-legend .ends { display: flex; justify-content: space-between; }
.drv-legend .lo { color: #a3360a; } .drv-legend .hi { color: var(--accent-ink); }
.drv { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: .75rem; align-items: center; padding: .45rem 0;
       border-top: 1px solid var(--line); }
.drv-name { display: flex; gap: .35rem; align-items: center; font-weight: 600; font-size: .92rem; line-height: 1.3; margin: 0; }
.drv-name .msr { font-size: 17px; flex: none; }
.drv.up .drv-name .msr { color: var(--accent-ink); } .drv.down .drv-name .msr { color: #a3360a; }
.drv-meta { color: var(--muted); font-size: .78rem; margin: .1rem 0 0 1.4rem; line-height: 1.35; font-family: var(--mono); }
.drv-meta b { color: var(--ink); font-weight: 500; }
.drv-track { position: relative; height: 14px; background: #eef1e8; }
.drv-track::after { content: ""; position: absolute; left: calc(50% - 1px); top: -3px; bottom: -3px; width: 2px; background: var(--ink-2); }
.drv-bar { position: absolute; top: 2px; bottom: 2px; width: calc(var(--w) * 50%); min-width: 4px; }
.drv.up .drv-bar { left: 50%; background: var(--accent); } .drv.down .drv-bar { right: 50%; background: #c2410c; }
.drv-str { font-family: var(--mono); font-size: .68rem; color: var(--ink-2); margin: .2rem 0 0; }
.drv.up .drv-str { text-align: right; } .drv.down .drv-str { text-align: left; }

.acts { display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: .8rem; margin: .4rem 0 .2rem; }
@media (max-width: 900px) { .acts { grid-template-columns: 1fr; } }
.act { display: flex; gap: .75rem; align-items: flex-start; background: var(--paper); border: 1px solid var(--line); border-top: 3px double var(--accent); padding: .8rem .9rem; }
.act-icon { flex: none; width: 36px; height: 36px; display: grid; place-items: center; color: var(--accent-ink); border: 1.5px solid var(--accent); border-radius: 50%; }
.act-icon .msr { font-size: 20px; }
.act-tag { font-family: var(--serif); font-style: italic; font-size: .85rem; color: var(--accent-ink); margin: 0; }
.act-title { font-family: var(--serif); font-weight: 700; font-size: 1.1rem; margin: .05rem 0 .3rem; }
.act-why { display: inline-flex; align-items: center; gap: .25rem; font-family: var(--mono); font-size: .74rem; color: var(--ink-2);
           border-bottom: 1px dashed var(--accent-tint); margin: 0 0 .4rem; }
.act-why .msr { font-size: 14px; color: var(--accent-ink); }
.act-text { color: var(--ink-2); font-size: .92rem; line-height: 1.55; margin: 0; }

/* 100 customers like this one: a sheet of stamps */
.people { display: grid; grid-template-columns: repeat(20, minmax(0, 1fr)); gap: 3px; margin: .5rem 0 .35rem; max-width: 440px;
          padding: 6px; border: 1px dashed var(--accent-tint); background: var(--paper); }
.person { aspect-ratio: 1; border-radius: 2px; background: #e6e8df; }
.person.yes { background: var(--band); }
.big-p { font-family: var(--mono); font-size: 3rem; font-weight: 500; line-height: 1; color: var(--ink); margin: .2rem 0 .1rem; }
.big-p small { font-family: var(--sans); font-size: 1rem; font-weight: 600; color: var(--muted); margin-left: .4rem; }
.people-cap { color: var(--ink-2); font-size: .9rem; margin: 0 0 .6rem; line-height: 1.45; }
.people-cap b { color: var(--ink); }
.pitch-channel { display: flex; gap: .8rem; align-items: flex-start; padding: .75rem .9rem; background: var(--band-soft);
                 border: 1px solid var(--band); border-left: 4px solid var(--band); margin: .3rem 0 .4rem; }
.pitch-channel .act-icon { background: #fff; color: var(--band-ink); border-color: var(--band); }

/* The campaign ledger */
.ledger { width: 100%; border-collapse: collapse; font-size: .93rem; background: var(--paper); }
.ledger th { font-family: var(--mono); font-size: .66rem; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 500;
             text-align: right; padding: .3rem .6rem; border-bottom: 1.5px solid var(--ink); }
.ledger th:first-child, .ledger td:first-child { text-align: left; }
.ledger td { padding: .38rem .6rem; border-bottom: 1px solid var(--rule); text-align: right; font-family: var(--mono); }
.ledger td:first-child { font-family: var(--sans); }
.ledger td small { display: block; font-family: var(--sans); font-size: .76rem; color: var(--muted); }
.ledger tr.sub td { border-top: 1px solid var(--ink); font-weight: 600; }
.ledger tr.total td { border-top: 1.5px solid var(--ink); border-bottom: 4px double var(--ink); font-weight: 700; font-size: 1.05rem; }
.ledger .neg { color: #a3360a; } .ledger .pos { color: var(--accent-ink); }

.footer { display: flex; gap: .9rem; align-items: center; color: var(--muted); font-size: .84rem; border-top: 4px double var(--accent);
          padding-top: 1rem; margin-top: 2.5rem; }
.footer-av { flex: none; width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--accent); color: var(--accent-ink);
             font-family: var(--serif); font-weight: 700; display: grid; place-items: center; font-size: .95rem; }
.footer a { color: var(--accent-ink); font-weight: 600; }
</style>
"""


def _css() -> str:
    return (CSS.replace("__ACCENT__", theme.ACCENT).replace("__INK__", theme.ACCENT_INK)
            .replace("__SOFT__", theme.ACCENT_SOFT).replace("__TINT__", theme.ACCENT_TINT))


def icon(name: str) -> str:
    """Material Symbols icon as HTML (the font Streamlit already loads)."""
    return f'<span class="msr" aria-hidden="true">{html.escape(name)}</span>'


def esc(text: str) -> str:
    """Escape $ so Streamlit markdown does not read amounts like $20 ... $70 as a LaTeX formula."""
    return text.replace("$", r"\$")


def md(text: str) -> None:
    st.markdown(esc(text))


def cap(text: str) -> None:
    st.caption(esc(text))


CONTROLS = """<style>
/* Controls: one shape, one border weight and one focus ring for every button, segment and input */
:root { --k-a: #0f7b5c; --k-a-text: #0a6249; --k-fill: #0f7b5c; --k-fill-2: #0a6249; --k-soft: #eef6f2; --k-ink: #1f2a24;
        --k-line: #b3bea9; --k-panel: #fffef8; --k-r: 2px; }
[data-testid="stMain"] :is([data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"],
  [data-testid="stBaseButton-secondaryFormSubmit"], [data-testid="stBaseButton-primaryFormSubmit"],
  [data-testid="stBaseButton-segmented_control"], [data-testid="stBaseButton-segmented_controlActive"],
  [data-testid="stBaseButton-pills"], [data-testid="stBaseButton-pillsActive"]) {
    border-radius: var(--k-r) !important; border: 1.5px solid var(--k-line) !important; background: var(--k-panel) !important;
    color: var(--k-ink) !important; box-shadow: none !important; min-height: 2.45rem; padding: .35rem .95rem !important;
    transition: border-color .12s ease, background-color .12s ease, color .12s ease; }
[data-testid="stMain"] :is([data-testid^="stBaseButton-secondary"], [data-testid^="stBaseButton-primary"],
  [data-testid^="stBaseButton-segmented_control"], [data-testid^="stBaseButton-pills"]) p {
    font-family: 'Public Sans', 'Segoe UI', sans-serif; font-size: .88rem; font-weight: 600; letter-spacing: 0; text-transform: none; color: inherit; }
[data-testid="stMain"] :is([data-testid^="stBaseButton-secondary"], [data-testid="stBaseButton-segmented_control"],
  [data-testid="stBaseButton-pills"]):hover { border-color: var(--k-a) !important; color: var(--k-a-text) !important; background: var(--k-soft) !important; }
[data-testid="stMain"] :is([data-testid^="stBaseButton-primary"], [data-testid="stBaseButton-segmented_controlActive"],
  [data-testid="stBaseButton-pillsActive"]) { background: var(--k-fill) !important; border-color: var(--k-fill) !important; color: #fff !important; }
[data-testid="stMain"] :is([data-testid^="stBaseButton-primary"], [data-testid="stBaseButton-segmented_controlActive"],
  [data-testid="stBaseButton-pillsActive"]):hover { background: var(--k-fill-2) !important; border-color: var(--k-fill-2) !important; color: #fff !important; }
[data-testid="stMain"] :is([data-testid^="stBaseButton-secondary"], [data-testid^="stBaseButton-primary"]):active { transform: translateY(1px); }
[data-testid="stMain"] [data-testid^="stBaseButton-"]:disabled { opacity: .45; }

/* Segmented controls: one joined strip, the chosen segment filled */
[data-testid="stMain"] [data-baseweb="button-group"] { gap: 0 !important; width: fit-content; max-width: 100%; border-radius: var(--k-r); }
[data-testid="stMain"] [data-baseweb="button-group"] > button { border-radius: 0 !important; margin: 0 0 0 -1.5px !important; position: relative;
    padding: .35rem .8rem !important; white-space: nowrap; }
[data-testid="stMain"] [data-baseweb="button-group"] > button:first-child { margin-left: 0 !important; border-radius: var(--k-r) 0 0 var(--k-r) !important; }
[data-testid="stMain"] [data-baseweb="button-group"] > button:last-child { border-radius: 0 var(--k-r) var(--k-r) 0 !important; }
[data-testid="stMain"] [data-baseweb="button-group"] > button:only-child { border-radius: var(--k-r) !important; }
[data-testid="stMain"] [data-baseweb="button-group"] > button:hover { z-index: 1; }
[data-testid="stMain"] [data-baseweb="button-group"] > [data-testid$="Active"] { z-index: 2; }

/* The focus ring: the same 2px ring, 2px off the edge, on every control (mouse click and keyboard alike) */
[data-testid="stMain"] [data-testid^="stBaseButton-"]:focus, [data-testid="stMain"] [data-testid^="stBaseButton-"]:focus-visible,
[data-testid="stPageLink"] a:focus-visible, [data-testid="stTopNavLink"]:focus-visible, [data-testid="stSidebarNavLink"]:focus-visible,
[data-testid="stMain"] [role="slider"]:focus-visible, [data-testid="stMain"] summary:focus-visible, [data-testid="stMain"] a:focus-visible {
    outline: 2px solid var(--k-a) !important; outline-offset: 2px; box-shadow: none !important; }
[data-testid="stMain"] [data-baseweb="button-group"] > button:focus, [data-testid="stMain"] [data-baseweb="button-group"] > button:focus-visible { outline: none !important; }
[data-testid="stMain"] [data-baseweb="button-group"]:focus-within { outline: 2px solid var(--k-a); outline-offset: 2px; }
[data-testid="stMain"] [data-testid="stCheckbox"] label:has(input:focus-visible) { outline: 2px solid var(--k-a); outline-offset: 3px; border-radius: var(--k-r); }

/* Inputs: square to the kit, a firm border, the accent border and ring while typing */
[data-testid="stMain"] :is([data-testid="stNumberInputContainer"], [data-testid="stTextInput"] [data-baseweb="input"],
  [data-testid="stDateInput"] [data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"]) {
    border-radius: var(--k-r) !important; border: 1.5px solid var(--k-line) !important; background: var(--k-panel) !important;
    min-height: 2.45rem; transition: border-color .12s ease; }
[data-testid="stMain"] :is([data-testid="stNumberInputContainer"], [data-testid="stTextInput"] [data-baseweb="input"],
  [data-baseweb="select"] > div, [data-baseweb="textarea"]):hover { border-color: var(--k-a) !important; }
[data-testid="stMain"] :is([data-testid="stNumberInputContainer"], [data-testid="stTextInput"] [data-baseweb="input"],
  [data-testid="stDateInput"] [data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"]):focus-within {
    border-color: var(--k-a) !important; outline: 2px solid var(--k-a); outline-offset: 2px; box-shadow: none !important; }
[data-testid="stMain"] :is([data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] > div, input, textarea) { background: transparent !important; }
[data-testid="stMain"] [data-testid="stNumberInputContainer"] [data-baseweb="input"] { border: none !important; }
[data-testid="stMain"] :is(input, textarea) { font-family: 'DM Mono', Consolas, monospace; color: var(--k-ink); }
[data-testid="stMain"] [data-testid="stNumberInputContainer"] > div:last-child { border-left: 1px solid var(--k-line); }
[data-testid="stMain"] :is([data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"]) { color: var(--k-ink) !important; border-radius: 0 !important; width: 2.1rem; }
[data-testid="stMain"] :is([data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"]):hover:not(:disabled) { background: var(--k-soft) !important; color: var(--k-a-text) !important; }
[data-testid="stMain"] [data-testid="stNumberInputStepUp"] { border-left: 1px solid var(--k-line) !important; }
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul[role="listbox"] { border-radius: var(--k-r) !important; border: 1.5px solid var(--k-line); }
[data-baseweb="popover"] li[role="option"]:hover, [data-baseweb="popover"] li[aria-selected="true"] { background: var(--k-soft) !important; color: var(--k-a-text); }

/* Labels, sliders, expanders and the file drop zone */
[data-testid="stMain"] [data-testid="stWidgetLabel"]:not([data-testid="stCheckbox"] *) p { font-family: 'DM Mono', Consolas, monospace; font-size: .72rem; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; color: #4a554f; }
[data-testid="stMain"] [data-baseweb="slider"] [role="slider"] { box-shadow: 0 0 0 3px var(--k-panel), 0 0 0 4.5px var(--k-fill) !important; }
[data-testid="stMain"] [data-testid="stSliderThumbValue"] { font-family: 'DM Mono', Consolas, monospace; font-weight: 600; }
[data-testid="stMain"] [data-testid="stExpander"] details { border: 1.5px solid var(--k-line) !important; border-radius: var(--k-r) !important; background: var(--k-panel); }
[data-testid="stMain"] [data-testid="stExpander"] summary:hover { color: var(--k-a-text); }
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] { border: 1.5px dashed var(--k-line) !important; border-radius: var(--k-r) !important; background: var(--k-panel) !important; }
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--k-a) !important; background: var(--k-soft) !important; }
[data-testid="stMain"] [data-testid="stAlert"] > div { border-radius: var(--k-r) !important; }
[data-baseweb="modal"] [role="dialog"] { border-radius: var(--k-r) !important; }
</style>"""


def inject_css() -> None:
    st.html(_css() + CONTROLS)


def header(kicker: str, title: str, lead: str, *, page_icon: str | None = None,
           chips: list[tuple[str, str]] | None = None) -> None:
    """Hero band at the top of every page. `chips` is a list of (icon, label)."""
    chip_html = ""
    if chips:
        chip_html = '<div class="chips">' + "".join(
            f'<span class="chip">{icon(i)}{html.escape(t)}</span>' for i, t in chips) + "</div>"
    st.html(
        f'<div class="hero"><div class="hero-icon">{icon(page_icon or theme.ICON)}</div><div class="hero-body">'
        f'<p class="kicker">{html.escape(kicker)}</p><h1>{html.escape(title)}</h1>'
        f'<p class="lead">{lead}</p>{chip_html}</div></div>'
    )


def insight(text: str) -> None:
    """Callout with the takeaway of the chart above. `text` may contain <b>."""
    st.html(f'<div class="insight"><div class="callout-icon">{icon("lightbulb")}</div><div>{text}</div></div>')


def note(text: str) -> None:
    """Amber callout for a caveat or a correction to the original analysis."""
    st.html(f'<div class="note"><div class="callout-icon">{icon("history_edu")}</div><div>{text}</div></div>')


def chart(fig, key: str | None = None) -> None:
    st.plotly_chart(fig, theme=None, config=CONFIG, key=key)


def section(title: str, question: str | None = None) -> None:
    st.subheader(title, anchor=False)
    if question:
        st.html(f'<p class="sec-q">{icon("help")}<span>{html.escape(question)}</span></p>')


def finding(col, big: str, big_label: str, title: str, text: str, page=None, link_label: str = "",
            card_icon: str = "insights") -> None:
    with col.container(border=True, height="stretch"):
        st.html(
            f'<div class="f-head"><div class="f-icon">{icon(card_icon)}</div></div>'
            f'<p class="big">{big}</p><p class="big-label">{big_label}</p>'
            f'<p class="card-title">{title}</p><p class="card-text">{text}</p>'
        )
        if page is not None:
            st.page_link(page, label=link_label, icon=":material/arrow_forward:")


def spotlight_box(title: str, text: str):
    """Bordered 'At a glance' box; returns the container so callers can add controls and charts."""
    box = st.container(border=True)
    box.html(f'<div class="spot"><span class="spot-tag">At a glance</span><p class="spot-title">'
             f'{html.escape(title)}</p></div><p class="spot-text">{text}</p>')
    return box


def spotlight(title: str, text: str, fig, key: str | None = None) -> None:
    """The one chart that tells the app's story, at the top of the findings page."""
    with spotlight_box(title, text):
        chart(fig, key=key)


def recommendations(items: list[tuple[str, str, str]]) -> None:
    """Numbered recommendation cards. Each item is (icon, title, text); text may contain <b>."""
    cards = "".join(
        f'<div class="rec"><div class="rec-head"><span class="rec-num">{n}</span>'
        f'<span class="msr rec-icon" aria-hidden="true">{html.escape(i)}</span></div>'
        f'<p class="rec-title">{t}</p><p class="rec-text">{x}</p></div>'
        for n, (i, t, x) in enumerate(items, 1)
    )
    st.html(f'<div class="recs" style="--n:{min(len(items), 4)}">{cards}</div>')


def method_card(text: str, page, tools: list[str] | None = None) -> None:
    """'How this was done' box with the tools used and a link to the method page."""
    chips = ""
    if tools:
        chips = '<div class="chips">' + "".join(f'<span class="chip">{html.escape(t)}</span>' for t in tools) + "</div>"
    with st.container(border=True):
        st.html(f'<div class="method"><div class="method-icon">{icon("science")}</div><div><p>{text}</p>{chips}'
                '</div></div>')
        st.page_link(page, label="Data & method", icon=":material/arrow_forward:")


def footer() -> None:
    st.html(
        '<div class="footer"><div class="footer-av">AH</div><div>Model and app by <b>Ahmad Hassan</b>, AI Engineer · '
        f'<a href="{NOTEBOOK_URL}" target="_blank">Notebook</a> · <a href="{CODE_URL}" target="_blank">App code</a> · '
        f'<a href="{LEARN_URL}" target="_blank">Learn with Ahmad</a><br>{DATA_CREDIT}</div></div>'
    )


def pct(p: float) -> str:
    """Probability as a whole percent (HTML-escaped), with '<1%' and '>99%' at the ends (never a misleading 0% or 100%)."""
    if p < 0.01:
        return "&lt;1%"
    if p > 0.99:
        return "&gt;99%"
    return f"{p:.0%}"


def chips(items: list[tuple[str, str]]) -> None:
    """A row of small (icon, label) chips."""
    st.html('<div class="chips derived">' + "".join(
        f'<span class="chip">{icon(i)}{html.escape(t)}</span>' for i, t in items) + "</div>")


def panel_head(n: int, title: str, sub: str) -> None:
    """Numbered heading for the result panels."""
    st.html(f'<div class="panel-head"><span class="panel-num">{n}</span><div><p class="panel-title">'
            f'{html.escape(title)}</p><p class="panel-sub">{sub}</p></div></div>')


def _band_style(band: str) -> str:
    r = theme.TIER[band]
    return f"--band:{r['color']};--band-ink:{r['ink']};--band-soft:{r['soft']}"


def band_pill(band: str) -> str:
    r = theme.TIER[band]
    return f'<span class="band" style="{_band_style(band)}">{icon(r["icon"])}{html.escape(r["label"])}</span>'


def verdict(band: str, text: str, rungs: list[tuple[str, str]], facts: list[tuple[str, str]]) -> None:
    """Tier pill, the verdict sentence, the three-step tier ladder (current step highlighted) and fact chips."""
    ladder = "".join(
        f'<div class="rung{" on" if name == band else ""}" style="{_band_style(name)}"><p class="rung-name">'
        f'{icon(theme.TIER[name]["icon"])}{html.escape(theme.TIER[name]["label"])}</p>'
        f'<p class="rung-range">{html.escape(rng)}</p></div>'
        for name, rng in rungs)
    chips_html = "".join(f'<span class="chip">{icon(i)}{html.escape(t)}</span>' for i, t in facts)
    st.html(f'<div class="score-top">{band_pill(band)}</div><p class="verdict-text">{text}</p>'
            f'<div class="ladder">{ladder}</div><div class="facts">{chips_html}</div>')


def drivers(rows: list[dict]) -> None:
    """Driver rows: name, this customer's value against a typical buyer, and a diverging bar.

    Each row: {"name", "value", "typical" (or ""), "shap"}. Bar length is relative to the largest |shap|.
    """
    biggest = max(abs(r["shap"]) for r in rows) or 1
    out = ['<div class="drv-legend"><span>Factor</span><span class="ends"><span class="lo">&#9664; lowers the chance</span>'
           '<span class="hi">raises the chance &#9654;</span></span></div>']
    for r in rows:
        up = r["shap"] > 0
        size = abs(r["shap"])
        strength = "strong" if size >= 1 else "moderate" if size >= 0.4 else "slight"
        typical = f' · typical buyer <b>{html.escape(r["typical"])}</b>' if r["typical"] else ""
        out.append(
            f'<div class="drv {"up" if up else "down"}"><div><p class="drv-name">'
            f'{icon("arrow_upward" if up else "arrow_downward")}{html.escape(r["name"])}</p>'
            f'<p class="drv-meta">This customer <b>{html.escape(r["value"])}</b>{typical}</p></div>'
            f'<div><div class="drv-track"><div class="drv-bar" style="--w:{size / biggest:.3f}"></div></div>'
            f'<p class="drv-str">{strength}, {"raises" if up else "lowers"} the chance</p></div></div>')
    st.html("".join(out))


def action_cards(items: list[tuple[str, str, str, str]], tag: str = "Angle") -> None:
    """Numbered cards. Each item is (icon, title, why, text); `why` is a short chip naming the fact it answers."""
    st.html(f'<div class="acts" style="--n:{max(len(items), 2)}">' + "".join(
        f'<div class="act"><div class="act-icon">{icon(i)}</div><div><p class="act-tag">{html.escape(tag)} {n}</p>'
        f'<p class="act-title">{html.escape(t)}</p>'
        + (f'<p class="act-why">{icon("person_check")}{html.escape(w)}</p>' if w else "")
        + f'<p class="act-text">{html.escape(x)}</p></div></div>'
        for n, (i, t, w, x) in enumerate(items, 1)) + "</div>")


def people(p: float, band: str, caption: str) -> None:
    """The probability as '100 customers like this one': a 20 x 5 dot grid with round(p * 100) dots filled."""
    n = int(round(p * 100))
    dots = "".join(f'<span class="person{" yes" if i < n else ""}"></span>' for i in range(100))
    st.html(f'<div style="{_band_style(band)}"><p class="big-p">{pct(p)}<small>chance of taking a personal loan</small>'
            f'</p><div class="people" role="img" aria-label="{n} of 100 similar customers">{dots}</div>'
            f'<p class="people-cap">{caption}</p></div>')


def pitch_channel(band: str, ic: str, title: str, text: str) -> None:
    """The recommended contact channel, coloured by the customer's tier."""
    st.html(f'<div class="pitch-channel" style="{_band_style(band)}"><div class="act-icon">{icon(ic)}</div><div>'
            f'<p class="act-tag" style="color:var(--band-ink)">How to reach them</p><p class="act-title">'
            f'{html.escape(title)}</p><p class="act-text">{html.escape(text)}</p></div></div>')


def ledger(rows: list[tuple[str, str, str, str, str]]) -> None:
    """The campaign as a ledger. Each row: (kind, item, detail, quantity, amount); kind is '' (a line), 'sub' or 'total'.
    Amounts are pre-formatted; a leading '-' shows in red, '+' in green."""
    out = []
    for kind, item, detail, qty, amount in rows:
        cls = "neg" if amount.startswith("-") else "pos" if amount.startswith("+") else ""
        d = f"<small>{detail}</small>" if detail else ""
        out.append(f'<tr class="{kind}"><td>{item}{d}</td><td>{qty}</td><td class="{cls}">{amount}</td></tr>')
    st.html('<table class="ledger"><thead><tr><th>Entry</th><th>Quantity</th><th>Amount</th></tr></thead><tbody>'
            + "".join(out) + "</tbody></table>")
