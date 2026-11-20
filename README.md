# LoanLift: personal loan campaign targeting application

**Live app:** [loanlift-campaign-application.streamlit.app](https://loanlift-campaign-application.streamlit.app/) · **Notebook and project folder:** [AIOPS-Portfolio-Projects](https://github.com/ahmadhassan-aiops/AIOPS-Portfolio-Projects/tree/main/2.%20Machine%20Learning%20Projects/ML%20project%20(Bank%20Loan%20Model))

A campaign-targeting tool for a bank's marketing team, by **Ahmad Hassan** (AI Engineer). Only 9.6% of AllLife
Bank's depositors took a personal loan in the last campaign. A tuned XGBoost pipeline, trained on 4,000 customers
and tested once on 1,000 it never saw, **finds 97% of the buyers, and 90% of the customers it targets take the
loan** (PR-AUC 0.991). The top 10% of scores hold 97% of the buyers.

The app looks like a **banker's ledger**: ruled ledger sheets with a red double margin, serif folios, rubber-stamp
labels, and the campaign itself written up as a ledger (contacts as spend, loans as income, the net result double
underlined).

- **Plan a campaign**: pick a customer list (the held-out customers, with their real response, or your own CSV),
  contact by score, by budget or by profit (cost per contact against value per loan), see the campaign ledger (spend, income, net against contacting everyone), the gains and profit curves, and download the ranked list with each customer's strongest reason.
- **Check a customer**: enter a profile; get the chance of a yes shown as "out of 100 customers like this", a tier,
  how many similar customers took the loan, the SHAP reasons, the contact channel and offer angles.
- **Who buys**: the segments behind the model (income × card spending, education × family size, products) and a
  segment builder.
- **Model performance**: held-out results, an interactive threshold trade-off, calibration and feature importance.
- **Data & method**: data, model search and limits.

## Why this stack

| Need | Choice |
|---|---|
| Interactive planning, what-if controls and charts for a marketing team | **Streamlit** (a Flask or Django front end would rebuild the same widgets by hand) |
| One artefact from raw record to probability, no training/serving skew | **scikit-learn `Pipeline`** saved with `joblib` |
| Best ranking on tabular data, calibrated probabilities, exact fast explanations | **XGBoost** with native SHAP values (`pred_contribs`); tied with gradient boosting and random forest in cross-validation, chosen for built-in explanations and a 1 MB file |
| Reject bad input before it reaches the model | **pydantic** schema for single customers and every row of an upload |
| Confidence that the shipped file is the evaluated model | **pytest** + GitHub Actions: predictions, test metrics, SHAP additivity, validation, campaign maths and every page |

The inference and campaign code (`loanlift/`) has no Streamlit dependency, so the same model can be served by an
API when a CRM or marketing platform needs to call it.

## How it is built

```
app.py                 entry point (top navigation)
nav.py                 page registry
views/                 one module per page
loanlift/schema.py     pydantic customer schema, labels, upload validation
loanlift/model.py      loads the pipeline, scores, explains (SHAP), tiers
loanlift/campaign.py   selection by threshold or budget, expected loans and profit, gains curve
loanlift/offers.py     contact channel and offer angles for a customer
lib/                   ledger UI kit (sheets, folios, stamps, campaign ledger), charts, theme, cached loaders, links
model/                 loan_propensity_xgb.joblib + metadata.json (threshold, metrics, versions)
data/                  held-out customers with scores, all customers, reference statistics
train.py               rebuilds model/ and data/ from the raw CSV
tests/                 model, schema, campaign and page tests
```

## Run locally

```bash
pip install -r requirements-dev.txt
pytest -q
streamlit run app.py
```

Rebuild the model from the dataset (same split, parameters and threshold as the notebook):

```bash
python train.py "path/to/Loan_Modelling.csv"
```

## Data

5,000 anonymised customers of AllLife Bank (a case-study bank) and their response to a past personal loan campaign.
The score says who is likely to want a loan, not who should get one. Predictions are a demonstration, not
financial advice.
