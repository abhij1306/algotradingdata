import pandas as pd, numpy as np
RUNS = '/data/workspace/hat-data-isin/backtests/runs'
R22 = '01a1864d-1b49-7316-aba6-d2c2d19fee21'
R16 = '01a17e77-8d4c-7499-bd40-fa621ba1f550'
CACHE = '/data/workspace/research/vcp-leaks/cache'
def load(run, name):
    df = pd.read_csv(f'{RUNS}/{run}/{name}.csv')
    for c in df.columns:
        if 'date' in c and c not in ('results_public_at',):
            df[c] = pd.to_datetime(df[c], errors='coerce')
    return df
def bars():
    b = pd.read_parquet(f'{CACHE}/adj.parquet')
    b['date'] = pd.to_datetime(b['date'])
    return b.sort_values(['instrument_id', 'date']).reset_index(drop=True)
