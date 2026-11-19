"""How to approach a customer: the contact channel (from the score) and offer angles (from their profile).

The angles are grounded in what the data shows about buyers: income, card spending, family size, education and
a CD account are what separate them. They are suggestions for the marketing team, not model outputs.
"""

from __future__ import annotations

from typing import Mapping

# (Material icon, title, text)
Offer = tuple[str, str, str]


def channel(p: float, threshold: float, online: bool) -> Offer:
    """Who should contact the customer and how, by how likely they are to say yes."""
    if p >= 0.9:
        return ("support_agent", "Personal call from a relationship manager",
                "Almost every customer scored this high took the loan in the last campaign. A direct call with a "
                "pre-approved offer is worth the time.")
    if p >= threshold:
        return ("forward_to_inbox", "Targeted offer, then a follow-up call",
                "A likely buyer. Send a personal offer " + ("in online banking and by email" if online else
                                                             "by post or in branch")
                + ", and follow up with a call if there is no reply within two weeks.")
    if p >= threshold / 3:
        return ("mark_email_unread", "Low-cost channel only",
                "Possible but not likely. Include them in an email or app banner campaign rather than calls.")
    return ("block", "Leave out of this campaign",
            "Very unlikely to take a loan now. Contacting them costs more than it is expected to bring in.")


def angles(c: Mapping[str, float], limit: int = 3) -> list[Offer]:
    """Offer angles that fit this customer's profile, most relevant first."""
    out: list[Offer] = []
    if c["CCAvg"] >= 2.5:
        out.append(("credit_card", "Consolidate card spending",
                    f"Spends ${c['CCAvg']:.1f}K a month on cards. A personal loan at a lower rate than card interest "
                    "is an easy saving to explain."))
    if c["Family"] >= 3:
        out.append(("family_restroom", "Family plans",
                    f"Family of {int(c['Family'])}. Frame the loan around family costs: school fees, a car, "
                    "a home project."))
    if c["CD_Account"]:
        out.append(("savings", "Preferred rate for CD holders",
                    "Already trusts the bank with a certificate of deposit. Offer a loyalty rate, or a loan secured "
                    "against the CD."))
    if c["Mortgage"] >= 100:
        out.append(("home", "Home improvement",
                    f"Has a ${c['Mortgage']:.0f}K mortgage. A home improvement loan fits homeowners without "
                    "remortgaging."))
    if c["Education"] >= 2 and c["Age"] < 40:
        out.append(("school", "Career and study",
                    "Graduate or professional early in their career: a loan for further study or a career move."))
    if not out:
        out.append(("payments", "General-purpose personal loan",
                    "No profile-specific angle stands out. Lead with rate, speed of approval and flexible terms."))
    return out[:limit]
