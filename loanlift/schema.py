"""What a customer record looks like: field names, labels, valid ranges and upload validation."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Model inputs, in the order the pipeline was trained with
FEATURES = ["Age", "Income", "Family", "CCAvg", "Education", "Mortgage",
            "Securities_Account", "CD_Account", "Online", "CreditCard"]
FLAGS = ["Securities_Account", "CD_Account", "Online", "CreditCard"]

LABELS = {
    "Age": "Age",
    "Income": "Annual income ($000)",
    "Family": "Family size",
    "CCAvg": "Card spending per month ($000)",
    "Education": "Education",
    "Mortgage": "Mortgage ($000)",
    "Securities_Account": "Securities account",
    "CD_Account": "Certificate of deposit (CD) account",
    "Online": "Uses online banking",
    "CreditCard": "Credit card from another bank",
}
SHORT = {  # compact names for charts and tables
    "Age": "Age", "Income": "Income", "Family": "Family size", "CCAvg": "Card spending", "Education": "Education",
    "Mortgage": "Mortgage", "Securities_Account": "Securities account", "CD_Account": "CD account",
    "Online": "Online banking", "CreditCard": "Card from another bank",
}
EDUCATION = {1: "Undergraduate", 2: "Graduate", 3: "Advanced / professional"}


class Customer(BaseModel):
    """One liability customer. Money is in thousands of dollars, as in the bank's data."""

    model_config = ConfigDict(extra="ignore")

    Age: int = Field(ge=18, le=100)
    Income: float = Field(ge=0, le=1000, description="Annual income, $000")
    Family: int = Field(ge=1, le=10)
    CCAvg: float = Field(ge=0, le=100, description="Average card spending per month, $000")
    Education: int = Field(ge=1, le=3)
    Mortgage: float = Field(ge=0, le=5000, description="Mortgage value, $000")
    Securities_Account: int = Field(ge=0, le=1)
    CD_Account: int = Field(ge=0, le=1)
    Online: int = Field(ge=0, le=1)
    CreditCard: int = Field(ge=0, le=1)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([self.model_dump()])[FEATURES]


def _message(err: dict) -> str:
    field = err["loc"][0] if err["loc"] else ""
    label = LABELS.get(field, field)
    msg = err["msg"].removeprefix("Value error, ")
    if err["type"] == "missing":
        msg = "missing"
    return f"{label}: {msg}" if label else msg


def validate_rows(raw: pd.DataFrame, max_errors: int = 10) -> tuple[pd.DataFrame, list[str]]:
    """Check every row of an uploaded list. Returns the clean model frame and readable errors ("Row 3: Age: ...").

    Missing columns are reported once. Rows with errors are left out of the frame.
    """
    missing = [c for c in FEATURES if c not in raw.columns]
    if missing:
        return pd.DataFrame(columns=FEATURES), ["Missing column(s): " + ", ".join(missing)]
    rows, errors, keep = [], [], []
    for i, record in enumerate(raw[FEATURES].to_dict("records")):
        try:
            rows.append(Customer(**{k: (None if pd.isna(v) else v) for k, v in record.items()}).model_dump())
            keep.append(raw.index[i])
        except ValidationError as exc:
            if len(errors) < max_errors:
                errors.append(f"Row {i + 1}: " + "; ".join(_message(e) for e in exc.errors()))
            elif len(errors) == max_errors:
                errors.append("More rows have errors; only the first ten are listed.")
    return pd.DataFrame(rows, columns=FEATURES, index=keep), errors
