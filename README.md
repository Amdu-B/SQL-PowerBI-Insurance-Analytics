# Insurance Sales Analytics — Portfolio Project

**Role target:** Data Analyst / BI Engineer — Generali Assicurazioni Italia  
**Stack:** Python · SQLite · SQL · Power BI (dashboard replicated as HTML/JS) · Excel  

---

## Project overview

End-to-end BI solution simulating the data pipeline of an insurance company's
sales network. Covers the full analyst workflow: raw data ingestion, cleaning,
SQL modelling, KPI calculation, and interactive dashboard delivery.

---

## Project structure

```
insurance_analytics/
│
├── data/
│   ├── raw/                       # Source files (as delivered by business)
│   │   ├── agents.xlsx            # 60 agents — region, seniority, target
│   │   ├── policies.xlsx          # 4,500 policies — product, premium, date
│   │   ├── claims.xlsx            # 548 claims — amounts, status
│   │   └── data_quality_log.xlsx  # QC log of flagged records
│   │
│   └── cleaned/                   # Validated datasets used in analytics
│       ├── agents_clean.xlsx
│       ├── policies_clean.xlsx    # 4,381 records after removing 119 dirty rows
│       └── claims_clean.xlsx
│
├── sql/
│   └── analysis_queries.sql       # 8 documented SQL queries
│
├── exports/
│   └── SQL_Query_Results.xlsx     # All query outputs (multi-sheet workbook)
│
├── insurance_analytics.db         # SQLite database
├── generate_data.py               # Synthetic data generator
└── build_sql.py                   # ETL pipeline + SQL runner
```

---

## Data model

```
agents ─────────────────────────────────────────────────────
  agent_id (PK) | name | surname | region | seniority
  hire_date | annual_target_eur | email

policies ───────────────────────────────────────────────────
  policy_id (PK) | agent_id (FK) | region | product_type
  issue_date | duration_months | premium_eur | status | client_age

claims ─────────────────────────────────────────────────────
  claim_id (PK) | policy_id (FK) | agent_id (FK) | region
  product_type | claim_date | claim_amount_eur | status
```

---

## SQL queries implemented

| Query | Purpose |
|-------|---------|
| Q1 — Annual summary | KPI cards: total premium, policies, avg premium |
| Q2 — Top 10 agents | Revenue ranking + target achievement % |
| Q3 — Product mix by year | Premium and volume by product line |
| Q4 — Regional performance | Premium per region and per agent |
| Q5 — Claim ratio | Loss ratio by product (risk KPI) |
| Q6 — Monthly trend 2024 | Time series for trend line chart |
| Q7 — Agent vs target 2024 | Full leaderboard with status flags |
| Q8 — Data quality check | Anomaly detection before analytics |

---

## Dashboard pages

| Page | Content |
|------|---------|
| Executive summary | Total premium KPIs, annual bar chart, policy status donut, monthly trend line |
| Sales network | Regional bar chart, seniority pie, agent leaderboard with target progress bars |
| Product mix | Premium donut by product, loss ratio horizontal bar |
| Data quality | QC metrics, flagged record log, clean vs dirty bar chart |

---

## Key findings

- **€4.35M** total premiums over 3 years across 60 agents and 8 Italian regions
- **Vita** is the highest-revenue product (€1.74M, 40% of mix) with the lowest loss ratio (8.7%)
- **Salute** carries the highest risk with a 64.6% loss ratio — key flag for underwriting
- **119 dirty records** (2.6% error rate) identified and removed before analytics
- **3 junior agents** exceeded their annual target in 2024 — strong performance signal
- **Piemonte** leads regional revenue (€855K), while **Emilia-Romagna** has the highest premium per agent (€77.9K)

---

## CV bullet point

> Designed and delivered an end-to-end insurance analytics solution processing 4,500+
> policy records from Excel/CSV sources. Built a normalised SQLite database, wrote 8
> SQL queries to compute revenue KPIs, agent rankings, claim ratios, and regional
> performance. Identified and documented 119 data quality anomalies (2.6% error rate).
> Visualised results in an interactive multi-page Power BI-style dashboard with
> drill-down across product mix, sales network, and time-series views.

---

## Tools & skills demonstrated

- **SQL** — JOINs, GROUP BY, CASE WHEN, window aggregates, LEFT JOIN for claims
- **Data quality** — anomaly detection, QC logging, clean/dirty record separation
- **Excel** — source data format matching real business inputs (agents.xlsx, policies.xlsx)
- **Power BI concepts** — KPI cards, slicers by region/seniority, trend lines, donut charts, leaderboard table
- **Python (ETL)** — pandas, sqlite3, openpyxl for pipeline automation
- **Business domain** — insurance KPIs: loss ratio, claim frequency, target achievement, premium per agent
