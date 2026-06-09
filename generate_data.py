import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('it_IT')
np.random.seed(42)
random.seed(42)

# ── CONFIG ─
REGIONS = ['Lombardia', 'Piemonte', 'Veneto', 'Lazio', 'Campania',
           'Sicilia', 'Toscana', 'Emilia-Romagna']

PRODUCT_TYPES = {
    'Auto RCA':        {'base_premium': 650,  'std': 180, 'claim_rate': 0.18},
    'Auto Kasko':      {'base_premium': 1200, 'std': 300, 'claim_rate': 0.12},
    'Vita':            {'base_premium': 2400, 'std': 800, 'claim_rate': 0.04},
    'Salute':          {'base_premium': 980,  'std': 200, 'claim_rate': 0.22},
    'Casa':            {'base_premium': 420,  'std': 120, 'claim_rate': 0.07},
    'Responsabilità':  {'base_premium': 310,  'std': 90,  'claim_rate': 0.05},
}

SENIORITY_LEVELS = ['Junior', 'Mid', 'Senior']

# ── 1. AGENTS ────────────────────────────────────────────────────────────────
def generate_agents(n=60):
    rows = []
    for i in range(1, n+1):
        seniority = random.choices(SENIORITY_LEVELS, weights=[0.35, 0.40, 0.25])[0]
        region    = random.choice(REGIONS)
        target    = {'Junior': 80000, 'Mid': 150000, 'Senior': 280000}[seniority]
        target   += random.randint(-10000, 10000)
        rows.append({
            'agent_id':    f'AG{i:03d}',
            'name':        fake.first_name(),
            'surname':     fake.last_name(),
            'region':      region,
            'seniority':   seniority,
            'hire_date':   fake.date_between(start_date='-12y', end_date='-6m'),
            'annual_target_eur': target,
            'email':       fake.email(),
        })
    return pd.DataFrame(rows)

# ── 2. POLICIES ──────────────────────────────────────────────────────────────
def generate_policies(agents_df, n=4500):
    rows = []
    start = datetime(2022, 1, 1)
    end   = datetime(2024, 12, 31)

    for i in range(1, n+1):
        product   = random.choice(list(PRODUCT_TYPES.keys()))
        cfg       = PRODUCT_TYPES[product]
        agent     = agents_df.sample(1).iloc[0]
        issue_dt  = fake.date_between(start_date=start, end_date=end)
        premium   = max(50, round(np.random.normal(cfg['base_premium'], cfg['std']), 2))
        duration  = random.choice([6, 12, 24])
        status    = random.choices(['Attiva', 'Scaduta', 'Annullata'], weights=[0.65, 0.28, 0.07])[0]

        # Introduce ~3% dirty rows for the data quality exercise
        if random.random() < 0.03:
            premium = -premium   # negative premium — data quality error

        rows.append({
            'policy_id':    f'POL{i:05d}',
            'agent_id':     agent['agent_id'],
            'region':       agent['region'],
            'product_type': product,
            'issue_date':   issue_dt,
            'duration_months': duration,
            'premium_eur':  premium,
            'status':       status,
            'client_age':   random.randint(18, 80),
        })
    return pd.DataFrame(rows)

# ── 3. CLAIMS ────────────────────────────────────────────────────────────────
def generate_claims(policies_df):
    rows = []
    active = policies_df[policies_df['premium_eur'] > 0]   # skip dirty rows
    claim_id = 1

    for _, pol in active.iterrows():
        cfg = PRODUCT_TYPES[pol['product_type']]
        if random.random() < cfg['claim_rate']:
            claim_dt = fake.date_between(
                start_date=pol['issue_date'],
                end_date=datetime(2024, 12, 31)
            )
            amount = round(pol['premium_eur'] * random.uniform(0.5, 4.5), 2)
            rows.append({
                'claim_id':      f'CLM{claim_id:05d}',
                'policy_id':     pol['policy_id'],
                'agent_id':      pol['agent_id'],
                'region':        pol['region'],
                'product_type':  pol['product_type'],
                'claim_date':    claim_dt,
                'claim_amount_eur': amount,
                'status':        random.choices(
                                    ['Liquidato', 'In Istruttoria', 'Rifiutato'],
                                    weights=[0.60, 0.28, 0.12])[0],
            })
            claim_id += 1
    return pd.DataFrame(rows)

# ── 4. DATA QUALITY LOG ──────────────────────────────────────────────────────
def generate_qc_log(policies_df):
    dirty = policies_df[policies_df['premium_eur'] < 0].copy()
    rows  = []
    for _, row in dirty.iterrows():
        rows.append({
            'check_date':    datetime.today().strftime('%Y-%m-%d'),
            'table':         'policies',
            'field':         'premium_eur',
            'policy_id':     row['policy_id'],
            'issue_found':   f'Premio negativo: {row["premium_eur"]}',
            'action_taken':  'Record escluso dal calcolo KPI',
            'status':        'Risolto',
            'analyst':       'Analista Dati',
        })
    return pd.DataFrame(rows)

# ── RUN 
print("⏳ Generating agents...")
agents_df   = generate_agents(60)

print("⏳ Generating policies...")
policies_df = generate_policies(agents_df, 4500)

print("⏳ Generating claims...")
claims_df   = generate_claims(policies_df)

print("⏳ Generating QC log...")
qc_df       = generate_qc_log(policies_df)

# Save raw files
agents_df.to_excel('/home/claude/insurance_analytics/data/raw/agents.xlsx',   index=False)
policies_df.to_excel('/home/claude/insurance_analytics/data/raw/policies.xlsx', index=False)
claims_df.to_excel('/home/claude/insurance_analytics/data/raw/claims.xlsx',   index=False)
qc_df.to_excel('/home/claude/insurance_analytics/data/raw/data_quality_log.xlsx', index=False)

print(f"\n Done!")
print(f"   Agents:   {len(agents_df)}")
print(f"   Policies: {len(policies_df)}  (dirty rows: {(policies_df['premium_eur']<0).sum()})")
print(f"   Claims:   {len(claims_df)}")
print(f"   QC rows:  {len(qc_df)}")
