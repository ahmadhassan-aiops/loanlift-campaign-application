"""
Chart styling and builders (Plotly), in the same style as the other apps.

Colour rules: one colour per single-series chart; emerald for customers who took the loan and warm grey for those
who did not (always labelled); a one-hue ramp for heatmaps; at most two series per chart, legend shown.
No pies, no dual axes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from lib.theme import ACCENT, BUYER, NONBUYER, SEQUENTIAL, SERIES_2

INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"

FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
CONFIG = {"displayModeBar": False, "scrollZoom": False}


def style(fig: go.Figure, *, height: int = 360, title: str | None = None, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=INK)) if title else None,
        font=dict(family=FONT, size=13, color=INK_2),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=8, r=16, t=48 if title else 16, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left", title=None),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, color=INK, size=13)),
        bargap=0.3,
    )
    fig.update_xaxes(automargin=True, showgrid=False, linecolor=AXIS, ticks="", tickfont=dict(color=MUTED),
                     title_font=dict(color=INK_2))
    fig.update_yaxes(automargin=True, gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont=dict(color=MUTED),
                     title_font=dict(color=INK_2))
    return fig


def _mark(fig: go.Figure, x: float, text: str) -> None:
    fig.add_vline(x=x, line=dict(color=INK, width=1.5, dash="dash"))
    fig.add_annotation(x=x, y=1.04, yref="paper", text=text, showarrow=False, font=dict(color=INK, size=12),
                       xanchor="left", xshift=4)


def gains(curve: pd.DataFrame, point: tuple[float, float], *, actual: bool) -> go.Figure:
    """Cumulative gains: % of customers contacted (best scores first) against % of loans reached, plus random."""
    what = "buyers reached" if actual else "expected loans reached"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random targeting",
                             line=dict(color=AXIS, width=1.5, dash="dot"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=curve["share_contacted"], y=curve["share_loans"], mode="lines", name="Targeted by LoanLift score",
        line=dict(color=ACCENT, width=3), fill="tozeroy", fillcolor="rgba(15,123,92,0.08)",
        customdata=curve["contacted"],
        hovertemplate=f"Contact %{{customdata:,}} customers (%{{x:.0%}})<br>%{{y:.0%}} of {what}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[point[0]], y=[point[1]], mode="markers+text", name="Your campaign",
        marker=dict(size=14, color=INK, line=dict(color=SURFACE, width=3)),
        text=[f"  {point[0]:.0%} contacted → {point[1]:.0%} of {what}"], textposition="middle right",
        textfont=dict(color=INK, size=13), hoverinfo="skip",
    ))
    style(fig, height=380, legend=True)
    fig.update_xaxes(title="Share of customers contacted, highest scores first", tickformat=".0%", range=[0, 1],
                     showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title=f"Share of {what}", tickformat=".0%", range=[0, 1.03])
    return fig


def profit(counts: np.ndarray, values: np.ndarray, chosen: int, best: int) -> go.Figure:
    """Expected profit against the number of customers contacted (best scores first), chosen and best marked."""
    fig = go.Figure(go.Scatter(
        x=counts, y=values, mode="lines", line=dict(color=ACCENT, width=2.5), name="Expected profit",
        hovertemplate="Contact %{x:,}<br>Expected profit $%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color=AXIS, width=1))
    fig.add_vline(x=best, line=dict(color=ACCENT, width=1.5, dash="dot"))
    fig.add_annotation(x=best, y=0.06, yref="paper", text=f"most profitable: {best:,}", showarrow=False,
                       font=dict(color=ACCENT, size=12), xanchor="left", xshift=6, bgcolor=SURFACE)
    _mark(fig, chosen, f"your plan: {chosen:,}")
    style(fig, height=300)
    fig.update_xaxes(title="Customers contacted (highest scores first)", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title="Expected profit", tickprefix="$", tickformat=",.0f")
    return fig


def score_histogram(proba: np.ndarray, threshold: float, outcome: np.ndarray | None = None) -> go.Figure:
    """How the list's probabilities are spread; split by real response when it is known. Log count axis."""
    bins = dict(start=0, end=1.0001, size=0.05)
    fig = go.Figure()
    if outcome is None:
        fig.add_trace(go.Histogram(x=proba, xbins=bins, name="Customers",
                                   marker=dict(color=ACCENT, line=dict(color=SURFACE, width=2)),
                                   hovertemplate="%{y:,} customers<extra></extra>"))
    else:
        for mask, name, color in ((outcome == 0, "Did not take the loan", NONBUYER),
                                  (outcome == 1, "Took the loan", BUYER)):
            fig.add_trace(go.Histogram(x=proba[mask], xbins=bins, name=name,
                                       marker=dict(color=color, line=dict(color=SURFACE, width=2)),
                                       hovertemplate=f"{name}: %{{y:,}}<extra></extra>"))
        fig.update_layout(barmode="group", bargroupgap=0.05)
    _mark(fig, threshold, f"contact from {threshold:.0%}")
    style(fig, height=300, legend=outcome is not None)
    fig.update_layout(bargap=0.08)
    fig.update_xaxes(title="Predicted probability of taking the loan", tickformat=".0%", range=[0, 1])
    fig.update_yaxes(title="Customers (log scale)", type="log", tickvals=[1, 10, 100, 1000],
                     ticktext=["1", "10", "100", "1,000"])
    return fig


def uptake_heatmap(rates: pd.DataFrame, counts: pd.DataFrame, x_title: str, y_title: str,
                   *, height: int = 330) -> go.Figure:
    """Loan uptake for every combination of two bands, one-hue ramp, rate and count in each cell."""
    z = rates.to_numpy(dtype=float)
    n = counts.reindex_like(rates).fillna(0).to_numpy(dtype=int)
    text = [[("" if c == 0 else f"<b>{r:.0%}</b><br>{c:,}") for r, c in zip(zr, zc)] for zr, zc in zip(z, n)]
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in rates.columns], y=[str(i) for i in rates.index], zmin=0, zmax=1,
        colorscale=SEQUENTIAL, showscale=False, xgap=3, ygap=3, text=text, texttemplate="%{text}",
        textfont=dict(size=12), customdata=n,
        hovertemplate=f"{x_title} %{{x}}<br>{y_title} %{{y}}<br>Uptake %{{z:.0%}} of %{{customdata:,}} customers"
                      "<extra></extra>",
    ))
    style(fig, height=height)
    fig.update_xaxes(title=x_title, side="bottom", tickfont=dict(color=INK_2), type="category")
    fig.update_yaxes(title=y_title, showgrid=False, tickfont=dict(color=INK_2), type="category")
    return fig


def uptake_bars(labels: list[str], rates: list[float], counts: list[int], average: float) -> go.Figure:
    """Uptake per group, single series, with the overall rate as a reference line."""
    fig = go.Figure(go.Bar(
        x=labels, y=rates, marker=dict(color=ACCENT, line=dict(width=0), cornerradius=4),
        text=[f"{r:.0%}" for r in rates], textposition="outside", cliponaxis=False, customdata=counts,
        hovertemplate="<b>%{x}</b><br>Uptake %{y:.1%} of %{customdata:,} customers<extra></extra>",
    ))
    fig.add_hline(y=average, line=dict(color=INK_2, width=1.2, dash="dot"))
    fig.add_annotation(x=1, xref="paper", y=1.08, yref="paper", text=f"dotted line: all customers {average:.1%}",
                       showarrow=False, xanchor="right", font=dict(size=12, color=INK_2))
    style(fig, height=320)
    fig.update_layout(margin=dict(t=36))
    fig.update_xaxes(tickangle=0)
    fig.update_yaxes(title="Took the loan", tickformat=".0%", rangemode="tozero")
    fig.update_xaxes(tickfont=dict(color=INK_2))
    return fig


def importance(labels: list[str], values: list[float]) -> go.Figure:
    """Mean |SHAP| per feature, single series, largest first."""
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=ACCENT, line=dict(width=0), cornerradius=4),
        hovertemplate="<b>%{y}</b><br>Average impact %{x:.2f} log-odds<extra></extra>",
    ))
    style(fig, height=30 * len(labels) + 70)
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=INK_2))
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title="Mean |SHAP| (log-odds)")
    return fig


def tradeoff(curve: pd.DataFrame, threshold: float) -> go.Figure:
    """Recall and precision against the decision threshold, with the chosen threshold marked."""
    fig = go.Figure()
    for col, color in (("Recall", ACCENT), ("Precision", SERIES_2)):
        fig.add_trace(go.Scatter(x=curve["threshold"], y=curve[col], name=col, mode="lines",
                                 line=dict(color=color, width=2), hovertemplate=f"{col} %{{y:.1%}}<extra></extra>"))
    _mark(fig, threshold, f"threshold {threshold:.2f}")
    style(fig, height=360, legend=True)
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(title="Decision threshold (contact customers at or above this probability)", range=[0, 1],
                     showspikes=True, spikecolor=AXIS, spikethickness=1, spikedash="solid")
    fig.update_yaxes(title="Held-out customers", tickformat=".0%", range=[0, 1.02])
    return fig


def confusion(tn: int, fp: int, fn: int, tp: int) -> go.Figure:
    """2x2 confusion matrix, one-hue ramp, counts and plain-language labels in each cell."""
    z = [[tn, fp], [fn, tp]]
    total = tn + fp + fn + tp
    names = [["No loan, not contacted", "No loan, contacted"], ["Took loan, missed", "Took loan, reached"]]
    shade = np.log1p(z) / np.log1p(max(tn, fp, fn, tp))
    fig = go.Figure(go.Heatmap(
        z=shade, x=["Not contacted", "Contacted"], y=["No loan", "Took the loan"], zmin=0, zmax=1,
        colorscale=SEQUENTIAL, showscale=False, xgap=3, ygap=3, hoverinfo="skip",
    ))
    for r, row in enumerate(["No loan", "Took the loan"]):
        for c, col in enumerate(["Not contacted", "Contacted"]):
            fig.add_annotation(x=col, y=row, showarrow=False,
                               font=dict(size=13, color="#ffffff" if shade[r][c] > 0.6 else INK),
                               text=f"<b>{z[r][c]:,}</b><br>{names[r][c]}<br>{z[r][c] / total:.1%}")
    style(fig, height=330)
    fig.update_yaxes(autorange="reversed", showgrid=False, title="What the customer did", tickfont=dict(color=INK_2))
    fig.update_xaxes(side="top", title="What the model said", tickfont=dict(color=INK_2))
    return fig


def calibration(predicted: list[float], observed: list[float], counts: list[int]) -> go.Figure:
    """Predicted against observed uptake per probability bin, with the perfect-calibration diagonal."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Perfectly calibrated",
                             line=dict(color=AXIS, width=1.5, dash="dot"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=predicted, y=observed, mode="lines+markers", name="This model",
        line=dict(color=ACCENT, width=2), marker=dict(size=9, color=ACCENT, line=dict(color=SURFACE, width=2)),
        customdata=counts,
        hovertemplate="Predicted %{x:.0%}<br>Actually took the loan %{y:.0%}<br>%{customdata:,} customers"
                      "<extra></extra>",
    ))
    style(fig, height=340, legend=True)
    fig.update_xaxes(title="Average predicted probability", tickformat=".0%", range=[0, 1], showgrid=True,
                     gridcolor=GRID)
    fig.update_yaxes(title="Share that took the loan", tickformat=".0%", range=[0, 1.02])
    return fig
