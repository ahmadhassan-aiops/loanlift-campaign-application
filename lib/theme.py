"""This app's colours and icon. Same family look as the other apps, with its own accent."""

ACCENT = "#0f7b5c"      # charts and highlights (emerald, 5.2:1 on the page background)
ACCENT_INK = "#0a6249"  # text in the accent colour
SERIES_2 = "#d4622a"    # second series (precision next to recall)
ICON = "real_estate_agent"  # Material Symbols name for the hero badge
HERO_MOTIF = ""         # extra CSS for the hero band, if any

# Likelihood tiers are status colours: always shown with a label and an icon, never colour alone
TIER = {
    "Prospect": {"label": "Prospect", "color": "#0f7b5c", "ink": "#0a6249", "soft": "#e6f3ee", "icon": "verified"},
    "Possible": {"label": "Possible", "color": "#b77800", "ink": "#8a5a00", "soft": "#fdf6e7", "icon": "help"},
    "Unlikely": {"label": "Unlikely", "color": "#6f6d68", "ink": "#52514e", "soft": "#f1f0ec", "icon": "do_not_disturb_on"},
}
RAISES = "#0f7b5c"   # SHAP bar that raises the likelihood of taking a loan
LOWERS = "#c2410c"   # SHAP bar that lowers it
BUYER = "#0f7b5c"    # customers who took the loan
NONBUYER = "#a8a69e" # customers who did not


def _mix(color: str, other: str, t: float) -> str:
    """Blend `color` towards `other` by t (0 = color, 1 = other)."""
    a = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


ACCENT_SOFT = _mix(ACCENT, "#ffffff", 0.92)   # callout and hero backgrounds
ACCENT_TINT = _mix(ACCENT, "#ffffff", 0.72)   # borders and decoration
QUIET = _mix(ACCENT, "#e4e4e0", 0.78)         # de-emphasised marks
SEQUENTIAL = [
    [0.0, _mix(ACCENT, "#ffffff", 0.95)], [0.35, _mix(ACCENT, "#ffffff", 0.6)], [0.7, ACCENT],
    [1.0, _mix(ACCENT, "#000000", 0.45)],
]
