# Bank Customer Churn Segmentation Analytics

Interactive Streamlit dashboard for analyzing retail banking customer churn through segmentation across geography, age, tenure, credit score, balance, and product usage. Built as part of a Data Analytics internship project.

## Overview

This project moves beyond a single aggregate churn rate to identify **where churn risk is concentrated** — by region, age group, financial profile, and engagement level — and quantifies the **revenue exposure** behind it, not just headcount.

**Type:** Data Analytics (descriptive & diagnostic segmentation analysis) — not a predictive ML model.

## Key Findings

- Overall churn rate: **20.37%**, but churned customers hold a disproportionate **24.26%** share of total deposit balances.
- Germany churns at **32.44%** — roughly double France and Spain — and this gap holds across every age group.
- The **46–60 / Germany** segment churns at **67.33%**, the single highest-risk combination in the dataset.
- Customers with **2 products** churn at just 7.58% (the low-risk sweet spot); 3–4 products show near-total or total churn.
- **Inactive members** churn at nearly double the rate of active members (26.85% vs. 14.27%).
- **Balance** — not salary — is a genuine churn driver; income shows no meaningful relationship to churn.

Full methodology and findings are documented in the accompanying research paper.

## Dashboard Modules

| Page | Contents |
|---|---|
| Overall Summary | Headline KPIs, churn split, Segment Churn Rate table, Geographic Risk Index, High-Value Churn Ratio, Engagement Drop Indicator |
| Geography | Churn rate & contribution by country, Geography × Age heatmap, drill-down by country, Financial Stability vs. Churn, Gender × Geography interaction |
| Age & Tenure | Churn rate by age group and tenure group, Age × Tenure heatmap |
| High-Value Customers | Adjustable balance threshold, churn-by-quartile, Definitions A/B robustness check, Balance vs. Salary comparison, revenue-at-risk breakdown |
| Segment Deep-Dive | Credit Score Band, Balance Segment, Gender, Number of Products, Active Membership, Churned vs. Retained profile comparison |

All pages respond live to the global sidebar filters (Geography, Gender, Age Group, Active Member status).

## KPIs Tracked

- **Overall Churn Rate** — % of customers who exited
- **Segment Churn Rate** — churn % by segment
- **High-Value Churn Ratio** — churn rate among high-balance customers vs. baseline
- **Geographic Risk Index** — regional churn rate ÷ overall baseline (1.0 = average risk)
- **Engagement Drop Indicator** — churn rate gap between inactive and active members

## Tech Stack

- [Streamlit](https://streamlit.io/) — dashboard framework
- [Pandas](https://pandas.pydata.org/) — data processing
- [Plotly](https://plotly.com/python/) — interactive charts

## Setup & Local Run

```bash
# clone the repo
git clone <your-repo-url>
cd churn_dashboard

# create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run the app
python -m streamlit run app.py
```

The app expects a CSV file in the project folder with the following columns:

```
CustomerId, Surname, CreditScore, Geography, Gender, Age, Tenure,
Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited
```

Update the `DATA_PATH` variable near the top of `app.py` to match your filename.

## Data Privacy Note

⚠️ **The raw customer dataset is not included in this repository** and should never be committed to version control, especially before deploying to a public host. See `.gitignore`.

If deploying to a public free host (e.g. Streamlit Community Cloud), do not expose row-level customer records (names, IDs) publicly. This dashboard drops `Surname` during load and is intended to be deployed with anonymized or aggregated data only — review any `st.dataframe(...)` calls showing row-level records before making the app public.

## Project Structure

```
churn_dashboard/
├── app.py              # Streamlit dashboard
├── requirements.txt     # Python dependencies
├── README.md
├── .gitignore
└── churn_data.csv       # (not committed — add your own)
```

## Deliverables

- Research paper (EDA, segmentation analysis, insights, recommendations)
- This Streamlit dashboard (live analytics)
- Executive summary for stakeholders

## Status

All Core Modules and User Capabilities (segment filters, dynamic KPIs, drill-down views) from the project requirements are implemented.
