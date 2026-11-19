"""Page furniture: CSS, hero header, callouts, cards, result panels and the footer.

The base is the kit shared with the analysis apps; the result panels (tier ladder, 100-customer grid, driver rows,
pitch cards) are this app's own.
"""

from __future__ import annotations

import html

import streamlit as st

from lib import theme
from lib.charts import CONFIG
from lib.site import CODE_URL, DATA_CREDIT, LEARN_URL, NOTEBOOK_URL

CSS = """
<style>
:root { --ink:#0b0b0b; --ink-2:#52514e; --muted:#6f6d68; --line:#e1e0d9; --surface:#fcfcfb;
        --accent:__ACCENT__; --accent-ink:__INK__; --accent-soft:__SOFT__; --accent-tint:__TINT__;
        --warn:#8a5a00; --warn-soft:#fdf6e7; }
.block-container { padding-top: 4.5rem; max-width: 1180px; }
h1, h2, h3 { color: var(--ink); letter-spacing: -0.01em; }
.msr { font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal; line-height: 1;
       letter-spacing: normal; text-transform: none; white-space: nowrap; direction: ltr; display: inline-block;
       -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased; }

/* Hero header */
.hero { position: relative; overflow: hidden; display: flex; gap: 1.25rem; align-items: flex-start;
        background: linear-gradient(135deg, var(--accent-soft) 0%, var(--surface) 72%);
        border: 1px solid var(--accent-tint); border-radius: 18px; padding: 1.6rem 1.75rem 1.5rem; margin: 0 0 1.5rem; }
.hero::after { content: ""; position: absolute; right: -40px; top: -40px; width: 260px; height: 260px; pointer-events: none;
               background-image: radial-gradient(var(--accent-tint) 1.6px, transparent 1.6px); background-size: 16px 16px;
               mask-image: radial-gradient(circle at 70% 30%, #000 0%, transparent 70%);
               -webkit-mask-image: radial-gradient(circle at 70% 30%, #000 0%, transparent 70%); }
__MOTIF__
.hero-icon { flex: none; width: 56px; height: 56px; border-radius: 16px; background: var(--accent); color: #fff;
             display: grid; place-items: center; box-shadow: 0 6px 18px -8px var(--accent); position: relative; z-index: 1; }
.hero-icon .msr { font-size: 32px; }
.hero-body { position: relative; z-index: 1; min-width: 0; }
.kicker { display: inline-flex; align-items: center; gap: .35rem; font-size: .74rem; font-weight: 700; text-transform: uppercase;
          letter-spacing: .08em; color: var(--accent-ink); background: #ffffffcc; border: 1px solid var(--accent-tint);
          border-radius: 999px; padding: .2rem .65rem; margin: 0 0 .6rem; }
.hero h1 { font-size: 2.15rem; line-height: 1.15; font-weight: 750; margin: 0 0 .5rem; padding: 0; }
.lead { font-size: 1.06rem; color: var(--ink-2); max-width: 800px; line-height: 1.62; margin: 0; }
.lead b { color: var(--ink); }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin: .9rem 0 0; }
.chip { display: inline-flex; align-items: center; gap: .3rem; font-size: .8rem; font-weight: 600; color: var(--ink-2);
        background: #fff; border: 1px solid var(--line); border-radius: 999px; padding: .22rem .65rem; }
.chip .msr { font-size: 16px; color: var(--accent-ink); }
@media (max-width: 640px) { .hero { flex-direction: column; padding: 1.25rem; } .hero h1 { font-size: 1.7rem; } }

/* Section headings get an accent bar; question captions become a soft pill */
[data-testid="stHeading"] h3 { border-left: 4px solid var(--accent); padding-left: .7rem; margin-top: .5rem; }
.sec-q { display: inline-flex; align-items: flex-start; gap: .4rem; color: var(--ink-2); font-size: .9rem; line-height: 1.45;
         background: var(--accent-soft); border-radius: 10px; padding: .4rem .75rem; margin: -.25rem 0 .75rem; }
.sec-q .msr { font-size: 18px; color: var(--accent-ink); margin-top: .02rem; }

/* Metrics: accent cap */
[data-testid="stMetric"] { position: relative; }
div[data-testid="stColumn"] [data-testid="stMetric"] { background: linear-gradient(180deg, var(--accent-soft) 0%, #ffffff00 85%);
        border-top: 3px solid var(--accent) !important; border-radius: 10px; }
[data-testid="stMetricValue"] { font-weight: 750; color: var(--ink); }
[data-testid="stMetricLabel"] p { color: var(--ink-2); font-weight: 600; }

/* Callouts */
.insight, .note { display: flex; gap: .7rem; align-items: flex-start; border-radius: 12px; padding: .85rem 1.1rem;
                  color: var(--ink); font-size: .98rem; line-height: 1.58; margin: .25rem 0 1.5rem; }
.insight { background: var(--accent-soft); border: 1px solid var(--accent-tint); }
.insight b { color: var(--accent-ink); }
.note { background: var(--warn-soft); border: 1px solid #f3dca8; font-size: .95rem; }
.callout-icon { flex: none; width: 30px; height: 30px; border-radius: 9px; display: grid; place-items: center; color: #fff; }
.insight .callout-icon { background: var(--accent); }
.note .callout-icon { background: #b77800; }
.callout-icon .msr { font-size: 19px; }

/* Finding cards */
.f-head { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
.f-icon { width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center; background: var(--accent-soft);
          color: var(--accent-ink); border: 1px solid var(--accent-tint); }
.f-icon .msr { font-size: 22px; }
.big { font-size: 2.1rem; font-weight: 780; color: var(--accent-ink); line-height: 1.1; margin: .6rem 0 0; }
.big-label { color: var(--muted); font-size: .85rem; margin: .15rem 0 .7rem; padding-bottom: .7rem; border-bottom: 1px dashed var(--line); }
.card-title { font-weight: 700; color: var(--ink); font-size: 1.03rem; margin: 0 0 .35rem; }
.card-text { color: var(--ink-2); font-size: .95rem; line-height: 1.55; margin: 0 0 .5rem; }
.card-text b { color: var(--ink); }
.verdict { font-weight: 650; }

/* Spotlight (signature chart) */
.spot { display: flex; align-items: center; flex-wrap: wrap; gap: .4rem .6rem; margin: 0 0 .2rem; }
.spot-tag { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #fff;
            background: var(--accent-ink); border-radius: 6px; padding: .18rem .5rem; white-space: nowrap; flex: none; }
.spot-title { font-size: 1.2rem; font-weight: 720; color: var(--ink); margin: 0; }
.spot-text { color: var(--ink-2); font-size: .95rem; line-height: 1.55; margin: .2rem 0 .25rem; max-width: 860px; }

/* Recommendations */
.recs { display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: .9rem; margin: .25rem 0 .9rem; }
@media (max-width: 900px) { .recs { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .recs { grid-template-columns: 1fr; } }
.rec { position: relative; background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1.1rem 1.05rem;
       border-top: 4px solid var(--accent); }
.rec-head { display: flex; align-items: center; gap: .6rem; margin-bottom: .55rem; }
.rec-num { width: 28px; height: 28px; border-radius: 50%; background: var(--accent); color: #fff; font-weight: 750;
           font-size: .9rem; display: grid; place-items: center; flex: none; }
.rec-icon { color: var(--accent-ink); font-size: 22px; margin-left: auto; }
.rec-title { font-weight: 700; color: var(--ink); font-size: 1rem; line-height: 1.35; margin: 0; }
.rec-text { color: var(--ink-2); font-size: .93rem; line-height: 1.55; margin: 0; }

/* Method card */
.method { display: flex; gap: .9rem; align-items: flex-start; }
.method-icon { flex: none; width: 42px; height: 42px; border-radius: 12px; display: grid; place-items: center;
               background: var(--ink); color: #fff; }
.method-icon .msr { font-size: 24px; }
.method p { color: var(--ink-2); font-size: .95rem; line-height: 1.58; margin: 0; }
.method p b { color: var(--ink); }

/* Markdown lists in the body: accent numbers */
[data-testid="stMarkdownContainer"] ol li::marker { color: var(--accent-ink); font-weight: 750; }
[data-testid="stMarkdownContainer"] ul li::marker { color: var(--accent); }

/* Result panels */
.band { display: inline-flex; align-items: center; gap: .3rem; font-weight: 750; font-size: .82rem; text-transform: uppercase;
        letter-spacing: .06em; color: var(--band-ink); background: var(--band-soft); border-radius: 999px; padding: .25rem .7rem; }
.band .msr { font-size: 18px; }
.derived { display: flex; gap: .5rem; flex-wrap: wrap; margin: .2rem 0 0; }

.panel-head { display: flex; gap: .7rem; align-items: center; margin: 0 0 .35rem; }
.panel-num { flex: none; width: 30px; height: 30px; border-radius: 9px; background: var(--ink); color: #fff; font-weight: 750;
             display: grid; place-items: center; font-size: .9rem; }
.panel-title { font-weight: 750; font-size: 1.1rem; color: var(--ink); margin: 0; line-height: 1.2; }
.panel-sub { color: var(--muted); font-size: .84rem; margin: .1rem 0 0; line-height: 1.35; }
.score-top { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; margin: .1rem 0 .3rem; }
.verdict-text { color: var(--ink-2); font-size: .95rem; line-height: 1.55; margin: .1rem 0 .75rem; }
.verdict-text b { color: var(--ink); }
.ladder { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .4rem; margin: 0 0 .7rem; }
.rung { border-radius: 10px; padding: .45rem .6rem; border: 1px solid var(--line); background: #fff; opacity: .6; }
.rung.on { opacity: 1; border: 2px solid var(--band); background: var(--band-soft); }
.rung-name { display: flex; align-items: center; gap: .3rem; font-weight: 750; font-size: .82rem; color: var(--band-ink); margin: 0; }
.rung-name .msr { font-size: 17px; }
.rung-range { font-size: .76rem; color: var(--ink-2); margin: .1rem 0 0; }
.facts { display: flex; flex-wrap: wrap; gap: .4rem; }

.drv-legend { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: .75rem; font-size: .72rem;
              font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin: .4rem 0 .15rem; }
.drv-legend .ends { display: flex; justify-content: space-between; }
.drv-legend .lo { color: #a3360a; }
.drv-legend .hi { color: var(--accent-ink); }
.drv { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: .75rem; align-items: center;
       padding: .55rem 0; border-top: 1px dashed var(--line); }
.drv-name { display: flex; gap: .35rem; align-items: center; font-weight: 650; color: var(--ink); font-size: .92rem;
            line-height: 1.3; margin: 0; }
.drv-name .msr { font-size: 18px; flex: none; }
.drv.up .drv-name .msr { color: var(--accent-ink); }
.drv.down .drv-name .msr { color: #a3360a; }
.drv-meta { color: var(--muted); font-size: .8rem; margin: .15rem 0 0 1.45rem; line-height: 1.35; }
.drv-meta b { color: var(--ink); font-weight: 700; }
.drv-track { position: relative; height: 16px; border-radius: 4px; background: #f3f2ee; }
.drv-track::after { content: ""; position: absolute; left: calc(50% - 1px); top: -3px; bottom: -3px; width: 2px;
                    background: var(--ink-2); }
.drv-bar { position: absolute; top: 2px; bottom: 2px; border-radius: 4px; width: calc(var(--w) * 50%); min-width: 4px; }
.drv.up .drv-bar { left: 50%; background: var(--accent); }
.drv.down .drv-bar { right: 50%; background: #c2410c; }
.drv-str { font-size: .72rem; color: var(--ink-2); margin: .2rem 0 0; font-weight: 600; }
.drv.up .drv-str { text-align: right; }
.drv.down .drv-str { text-align: left; }

.acts { display: grid; grid-template-columns: repeat(var(--n, 3), minmax(0, 1fr)); gap: .8rem; margin: .4rem 0 .2rem; }
@media (max-width: 900px) { .acts { grid-template-columns: 1fr; } }
.act { display: flex; gap: .8rem; align-items: flex-start; background: #fff; border: 1px solid var(--line);
       border-top: 4px solid var(--accent); border-radius: 12px; padding: .9rem 1rem; }
.act-icon { flex: none; width: 42px; height: 42px; border-radius: 12px; background: var(--accent-soft); color: var(--accent-ink);
            border: 1px solid var(--accent-tint); display: grid; place-items: center; }
.act-icon .msr { font-size: 24px; }
.act-tag { font-size: .7rem; font-weight: 750; text-transform: uppercase; letter-spacing: .07em; color: var(--accent-ink); margin: 0; }
.act-title { font-weight: 720; color: var(--ink); font-size: 1rem; margin: .1rem 0 .3rem; }
.act-why { display: inline-flex; align-items: center; gap: .25rem; font-size: .8rem; color: var(--ink-2); background: var(--accent-soft);
           border-radius: 6px; padding: .15rem .5rem; margin: 0 0 .4rem; }
.act-why .msr { font-size: 15px; color: var(--accent-ink); }
.act-text { color: var(--ink-2); font-size: .92rem; line-height: 1.55; margin: 0; }

/* 100 customers like this one */
.people { display: grid; grid-template-columns: repeat(20, minmax(0, 1fr)); gap: 3px; margin: .5rem 0 .35rem; max-width: 420px; }
.person { aspect-ratio: 1; border-radius: 50%; background: #e4e3dd; }
.person.yes { background: var(--band); }
.big-p { font-size: 3rem; font-weight: 800; line-height: 1; color: var(--ink); margin: .2rem 0 .1rem; }
.big-p small { font-size: 1rem; font-weight: 650; color: var(--muted); margin-left: .35rem; }
.people-cap { color: var(--ink-2); font-size: .88rem; margin: 0 0 .6rem; line-height: 1.45; }
.people-cap b { color: var(--ink); }
.pitch-channel { display: flex; gap: .8rem; align-items: flex-start; border-radius: 12px; padding: .85rem 1rem;
                 background: var(--band-soft); border: 1px solid var(--band); margin: .3rem 0 .2rem; }
.pitch-channel .act-icon { background: #fff; color: var(--band-ink); border-color: var(--band); }

.footer { display: flex; gap: .9rem; align-items: center; color: var(--muted); font-size: .85rem; border-top: 1px solid var(--line);
          padding-top: 1.1rem; margin-top: 2.75rem; }
.footer-av { flex: none; width: 40px; height: 40px; border-radius: 50%; background: var(--accent); color: #fff; font-weight: 750;
             display: grid; place-items: center; font-size: .9rem; }
.footer a { color: var(--ink-2); font-weight: 600; }
</style>
"""


def _css() -> str:
    return (CSS.replace("__ACCENT__", theme.ACCENT).replace("__INK__", theme.ACCENT_INK)
            .replace("__SOFT__", theme.ACCENT_SOFT).replace("__TINT__", theme.ACCENT_TINT)
            .replace("__MOTIF__", theme.HERO_MOTIF))


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


def inject_css() -> None:
    st.html(_css())


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
