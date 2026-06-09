-- ============================================================
--  INSURANCE SALES ANALYTICS — SQL QUERIES
--  Project: Generali Assicurazioni Portfolio Analysis
--  Author:  Amdu Berga Moshiye
--  DB:      SQLite (insurance_analytics.db)
--  Tables:  agents | policies | claims
-- ============================================================


-- Q1: ANNUAL SUMMARY 
-- High-level KPIs per year for the executive summary page

SELECT
    year,
    COUNT(policy_id)            AS total_policies,
    ROUND(SUM(premium_eur), 2)  AS total_premium_eur,
    ROUND(AVG(premium_eur), 2)  AS avg_premium_eur,
    COUNT(DISTINCT agent_id)    AS active_agents
FROM policies
GROUP BY year
ORDER BY year;


-- Q2: TOP 10 AGENTS BY TOTAL REVENUE 
-- Ranks agents by premium generated; calculates target achievement %

SELECT
    p.agent_id,
    a.name || ' ' || a.surname         AS agent_name,
    a.region,
    a.seniority,
    a.annual_target_eur,
    COUNT(p.policy_id)                 AS policies_sold,
    ROUND(SUM(p.premium_eur), 2)       AS total_premium_eur,
    ROUND(
        SUM(p.premium_eur) / a.annual_target_eur * 100,
    1)                                 AS target_achievement_pct
FROM policies p
JOIN agents a ON p.agent_id = a.agent_id
GROUP BY p.agent_id
ORDER BY total_premium_eur DESC
LIMIT 10;


--Q3: PRODUCT MIX BY YEAR 
-- Breaks down volume and revenue by product line for trend analysis

SELECT
    product_type,
    year,
    COUNT(policy_id)            AS policies,
    ROUND(SUM(premium_eur), 2)  AS total_premium_eur,
    ROUND(AVG(premium_eur), 2)  AS avg_premium_eur
FROM policies
GROUP BY product_type, year
ORDER BY product_type, year;


-- Q4: REGIONAL PERFORMANCE 
-- Compares total output and efficiency across regions

SELECT
    region,
    COUNT(policy_id)                                   AS total_policies,
    ROUND(SUM(premium_eur), 2)                         AS total_premium_eur,
    COUNT(DISTINCT agent_id)                           AS agents,
    ROUND(SUM(premium_eur) / COUNT(DISTINCT agent_id), 2)
                                                       AS premium_per_agent
FROM policies
GROUP BY region
ORDER BY total_premium_eur DESC;


-- Q5: CLAIM RATIO BY PRODUCT 
-- Key risk metric: loss ratio = claims paid / premiums collected
-- Used by underwriting and risk departments

SELECT
    p.product_type,
    COUNT(DISTINCT p.policy_id)               AS total_policies,
    COUNT(DISTINCT c.claim_id)                AS total_claims,
    ROUND(SUM(c.claim_amount_eur), 2)         AS total_claims_eur,
    ROUND(SUM(p.premium_eur), 2)              AS total_premium_eur,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0
        / COUNT(DISTINCT p.policy_id),
    1)                                        AS claim_frequency_pct,
    ROUND(
        COALESCE(SUM(c.claim_amount_eur), 0)
        / SUM(p.premium_eur) * 100,
    1)                                        AS loss_ratio_pct
FROM policies p
LEFT JOIN claims c ON p.policy_id = c.policy_id
GROUP BY p.product_type
ORDER BY loss_ratio_pct DESC;


-- Q6: MONTHLY TREND 2024
-- Used to populate the monthly trend line chart in Power BI

SELECT
    year_month,
    COUNT(policy_id)            AS policies_sold,
    ROUND(SUM(premium_eur), 2)  AS monthly_premium_eur
FROM policies
WHERE year = 2024
GROUP BY year_month
ORDER BY year_month;


-- Q7: AGENT VS TARGET — 2024 
-- Full agent leaderboard with target status flags
-- Useful for sales management reporting

SELECT
    a.agent_id,
    a.name || ' ' || a.surname                         AS agent_name,
    a.region,
    a.seniority,
    a.annual_target_eur,
    ROUND(SUM(p.premium_eur), 2)                       AS actual_premium_eur,
    ROUND(SUM(p.premium_eur) - a.annual_target_eur, 2) AS gap_eur,
    ROUND(
        SUM(p.premium_eur) / a.annual_target_eur * 100,
    1)                                                 AS achievement_pct,
    CASE
        WHEN SUM(p.premium_eur) >= a.annual_target_eur
            THEN 'Target Raggiunto'
        WHEN SUM(p.premium_eur) >= a.annual_target_eur * 0.80
            THEN 'Quasi Target'
        ELSE 'Sotto Target'
    END                                                AS target_status
FROM agents a
LEFT JOIN policies p
    ON a.agent_id = p.agent_id AND p.year = 2024
GROUP BY a.agent_id
ORDER BY achievement_pct DESC;


-- Q8: DATA QUALITY CHECK
-- Identifies records with data anomalies before they enter analytics

SELECT
    policy_id,
    agent_id,
    product_type,
    premium_eur,
    'Negative premium — excluded from KPI' AS issue_description
FROM policies
WHERE premium_eur < 0

UNION ALL

SELECT
    policy_id,
    agent_id,
    product_type,
    premium_eur,
    'Zero premium — excluded from KPI' AS issue_description
FROM policies
WHERE premium_eur = 0

ORDER BY policy_id;
