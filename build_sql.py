"""
STEP 2 — SQL Layer
Loads cleaned data into SQLite and runs all analytical queries.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = '/home/claude/insurance_analytics/insurance_analytics.db'
RAW     = '/home/claude/insurance_analytics/data/raw'
CLEAN   = '/home/claude/insurance_analytics/data/cleaned'

# ── LOAD RAW DATA 
agents_df   = pd.read_excel(f'{RAW}/agents.xlsx')
policies_df = pd.read_excel(f'{RAW}/policies.xlsx')
claims_df   = pd.read_excel(f'{RAW}/claims.xlsx')

# ── DATA CLEANING 
print("🧹 Cleaning data...")

# Remove negative premiums (flagged in QC log)
policies_clean = policies_df[policies_df['premium_eur'] > 0].copy()
policies_clean['issue_date'] = pd.to_datetime(policies_clean['issue_date'])
policies_clean['year']       = policies_clean['issue_date'].dt.year
policies_clean['month']      = policies_clean['issue_date'].dt.month
policies_clean['year_month'] = policies_clean['issue_date'].dt.to_period('M').astype(str)

agents_clean = agents_df.copy()
agents_clean['hire_date'] = pd.to_datetime(agents_clean['hire_date'])

claims_clean = claims_df.copy()
claims_clean['claim_date'] = pd.to_datetime(claims_clean['claim_date'])
claims_clean['year']       = claims_clean['claim_date'].dt.year

# Save cleaned files
policies_clean.to_excel(f'{CLEAN}/policies_clean.xlsx', index=False)
agents_clean.to_excel(f'{CLEAN}/agents_clean.xlsx',     index=False)
claims_clean.to_excel(f'{CLEAN}/claims_clean.xlsx',     index=False)

print(f"   Policies after cleaning: {len(policies_clean)} (removed {len(policies_df)-len(policies_clean)} dirty rows)")

# ── BUILD SQLITE DB 
print("\n  Building SQLite database...")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)

agents_clean.to_sql('agents',   conn, if_exists='replace', index=False)
policies_clean.to_sql('policies', conn, if_exists='replace', index=False)
claims_clean.to_sql('claims',   conn, if_exists='replace', index=False)
print("   Tables created: agents, policies, claims")

# ── SQL QUERIES 
queries = {}

# Q1 — Total premiums and policies by year
queries['Q1_annual_summary'] = """
SELECT
    year,
    COUNT(policy_id)            AS total_policies,
    ROUND(SUM(premium_eur), 2)  AS total_premium_eur,
    ROUND(AVG(premium_eur), 2)  AS avg_premium_eur,
    COUNT(DISTINCT agent_id)    AS active_agents
FROM policies
GROUP BY year
ORDER BY year;
"""

# Q2 — Top 10 agents by revenue (all years)
queries['Q2_top10_agents'] = """
SELECT
    p.agent_id,
    a.name || ' ' || a.surname   AS agent_name,
    a.region,
    a.seniority,
    a.annual_target_eur,
    COUNT(p.policy_id)           AS policies_sold,
    ROUND(SUM(p.premium_eur), 2) AS total_premium_eur,
    ROUND(SUM(p.premium_eur) / a.annual_target_eur * 100, 1) AS target_achievement_pct
FROM policies p
JOIN agents a ON p.agent_id = a.agent_id
GROUP BY p.agent_id
ORDER BY total_premium_eur DESC
LIMIT 10;
"""

# Q3 — Premium by product type and year
queries['Q3_product_mix'] = """
SELECT
    product_type,
    year,
    COUNT(policy_id)            AS policies,
    ROUND(SUM(premium_eur), 2)  AS total_premium_eur,
    ROUND(AVG(premium_eur), 2)  AS avg_premium_eur
FROM policies
GROUP BY product_type, year
ORDER BY product_type, year;
"""

# Q4 — Regional performance
queries['Q4_regional_performance'] = """
SELECT
    p.region,
    COUNT(p.policy_id)            AS total_policies,
    ROUND(SUM(p.premium_eur), 2)  AS total_premium_eur,
    COUNT(DISTINCT p.agent_id)    AS agents,
    ROUND(SUM(p.premium_eur) / COUNT(DISTINCT p.agent_id), 2) AS premium_per_agent
FROM policies p
GROUP BY p.region
ORDER BY total_premium_eur DESC;
"""

# Q5 — Claim ratio by product type
queries['Q5_claim_ratio'] = """
SELECT
    p.product_type,
    COUNT(DISTINCT p.policy_id)           AS total_policies,
    COUNT(DISTINCT c.claim_id)            AS total_claims,
    ROUND(SUM(c.claim_amount_eur), 2)     AS total_claims_eur,
    ROUND(SUM(p.premium_eur), 2)          AS total_premium_eur,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0 / COUNT(DISTINCT p.policy_id),
    1)                                    AS claim_frequency_pct,
    ROUND(
        COALESCE(SUM(c.claim_amount_eur), 0) / SUM(p.premium_eur) * 100,
    1)                                    AS loss_ratio_pct
FROM policies p
LEFT JOIN claims c ON p.policy_id = c.policy_id
GROUP BY p.product_type
ORDER BY loss_ratio_pct DESC;
"""

# Q6 — Monthly trend 2024
queries['Q6_monthly_trend_2024'] = """
SELECT
    year_month,
    COUNT(policy_id)            AS policies_sold,
    ROUND(SUM(premium_eur), 2)  AS monthly_premium_eur
FROM policies
WHERE year = 2024
GROUP BY year_month
ORDER BY year_month;
"""

# Q7 — Agent performance vs target (2024)
queries['Q7_agent_vs_target_2024'] = """
SELECT
    a.agent_id,
    a.name || ' ' || a.surname            AS agent_name,
    a.region,
    a.seniority,
    a.annual_target_eur,
    ROUND(SUM(p.premium_eur), 2)          AS actual_premium_eur,
    ROUND(SUM(p.premium_eur) - a.annual_target_eur, 2) AS gap_eur,
    ROUND(SUM(p.premium_eur) / a.annual_target_eur * 100, 1) AS achievement_pct,
    CASE
        WHEN SUM(p.premium_eur) >= a.annual_target_eur THEN ' Target Raggiunto'
        WHEN SUM(p.premium_eur) >= a.annual_target_eur * 0.80 THEN '⚠️ Quasi Target'
        ELSE '❌ Sotto Target'
    END AS target_status
FROM agents a
LEFT JOIN policies p ON a.agent_id = p.agent_id AND p.year = 2024
GROUP BY a.agent_id
ORDER BY achievement_pct DESC;
"""

# ── RUN AND SAVE RESULTS 
print("\n Running SQL queries...")

results = {}
for name, sql in queries.items():
    df = pd.read_sql_query(sql, conn)
    results[name] = df
    print(f"   {name}: {len(df)} rows")

# Save all query results into a single Excel workbook (multi-sheet)
output_path = '/home/claude/insurance_analytics/exports/SQL_Query_Results.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    for name, df in results.items():
        df.to_excel(writer, sheet_name=name[:31], index=False)

conn.close()
print(f"\n SQL layer complete!")
print(f"   Database: {DB_PATH}")
print(f"   Query results exported: {output_path}")
