# Backtest Result Standard v1.0

Every backtest run writes one folder. No exceptions, no partial runs.

```
runs/<run_id>/
  run.json        # identity, config, headline metrics, breakdowns  (schema: run.schema.json)
  trades.csv      # one row per closed trade, with setup + stock features at entry
  equity.csv      # one row per session
  refusals.csv    # one row per blocked entry, with the same features
  signals.csv     # every setup that fired, taken or not
  stocks.csv      # one row per symbol: how S1 did on that stock
```

Why four files: headline metrics say *whether* a variant is better. Trades, equity and refusals say *why*, and that is what tweak suggestions are built from.

---

## 1. run.json

### identity
- `run_id`: unique, sortable (current hex ids are fine)
- `strategy`: `S1` (Minervini), `S2` (Qullamaggie), and so on
- `strategy_version`: code hash of the strategy (e.g. `aac4fda7`)
- `engine_commit`: git commit of the repo
- `sweep_id`, `sweep_name`, `variant`: e.g. `sweep-07`, `policy v3 on np`, `v3-np`
- `base_run_id`: run this variant is compared against (null for a baseline)
- `change`: one line, plain words (e.g. `+ RS rank ≥ 70`)
- `created_at`, `status` (`complete` | `failed` | `stopped_early`)

### data
- `universe`: e.g. `NIFTY500_PIT`
- `data_snapshot_id`: price data version; reruns must match
- `split`: `in_sample` | `hold_out`
- `period_start`, `period_end`
- `benchmark`: e.g. `NIFTY500_TRI`

### config
- `overrides`: only the parameters changed vs `base_run_id`
- `resolved`: full parameter set as actually run (setup, entry, exits, regime, risk policy)
- `resolved_hash`: hash of `resolved`; two runs with the same hash are duplicates
- `cost_model`: version id of the dated cost table
- `start_capital`

### metrics (all net of costs)
| field | definition |
|---|---|
| `trades` | closed trades |
| `signals` | setups that fired before any risk gate |
| `win_pct` | trades with net R > 0 ÷ trades |
| `avg_win_r`, `avg_loss_r` | mean net R of winners / losers |
| `expectancy_r` | mean net R over all trades |
| `avg_mfe_r`, `avg_mae_r` | mean best / worst open R reached |
| `cagr_pct` | (final ÷ start)^(365.25 ÷ calendar days) − 1 |
| `max_dd_pct` | largest peak-to-trough fall in daily closing equity |
| `mar` | cagr_pct ÷ max_dd_pct |
| `sharpe` | annualised daily, √252; `rf_pct` stated |
| `sortino` | annualised daily, downside deviation only |
| `invested_pct` | mean of daily (position value ÷ equity) |
| `avg_open_positions` | mean of daily open positions |
| `longest_dd_sessions` | peak to recovery; to period end if never recovered |
| `longest_dd_recovered` | true / false |
| `longest_dd_start`, `longest_dd_end` | dates |
| `dsr_prob` | deflated Sharpe probability |
| `dsr_n_trials` | variants counted for DSR; required, or DSR is meaningless |
| `total_return_pct`, `final_equity` | |
| `fees` | all costs in ₹ |
| `cost_share_pct` | fees ÷ gross profit, where gross = net P&L + fees; null if gross ≤ 0 |
| `benchmark_cagr_pct` | benchmark over the same period |
| `avg_hold_sessions_win`, `avg_hold_sessions_loss` | |
| `max_consecutive_losses` | |
| `symbols_traded` | distinct symbols with at least one trade |
| `top5_trades_pnl_share_pct` | net P&L of the 5 best trades ÷ total net P&L |
| `top10_symbols_pnl_share_pct` | net P&L of the 10 best symbols ÷ total net P&L |
| `cagr_ex_top5_trades_pct` | CAGR with the 5 best trades removed (their P&L set to 0) |
| `max_position_pct_adv` | largest entry size ÷ 20-day average traded value |
| `trades_over_5pct_adv` | entries above 5% of 20-day average traded value (fill not realistic) |

### refusals
`{reason: count}`. Fixed reason codes: `max_positions`, `ladder_level`, `industry_cap`, `size_zero_cash`, `size_zero_risk`, `max_chase`, `stopout_cap`, `open_risk_cap`, `regime_off`, `kill_switch`.

### binding
Whether the change actually did anything. Required for every variant with a base.
- `trades_changed`: entries different from the base run
- `trade_list_hash`: hash of (symbol, entry_date, exit_date); same hash as base = the change never triggered
- `no_op`: true when the trade list hash matches the base

### breakdowns
- `by_year`: per calendar year: return %, max DD %, trades, expectancy R, benchmark return %
- `by_regime`: per regime state at entry (index on/off, breadth bucket): trades, win %, expectancy R
- `by_exit_reason`: per exit reason: trades, avg R, avg hold sessions
- `by_industry`: per industry: trades, win %, expectancy R, net P&L
- `by_cap_bucket`: `large` | `mid` | `small` | `micro` at entry: trades, win %, expectancy R
- `by_liquidity_bucket`: 20-day average traded value quintile at entry: trades, win %, expectancy R

---

## 2. trades.csv

One row per closed trade. Partial exits: one row per leg, sharing `trade_id`.

```
run_id,trade_id,leg,symbol,industry,
signal_date,entry_date,entry_price,initial_stop,risk_per_share,qty,risk_pct_equity,
exit_date,exit_price,exit_reason,hold_sessions,
gross_pnl,fees,net_pnl,r_net,mfe_r,mae_r,mfe_date,
mcap_cr,cap_bucket,index_membership,adv_20d_cr,position_pct_adv,price,listing_age_years,
prior_trades_symbol,prior_stopouts_symbol_90d,
ladder_level,open_positions_at_entry,open_risk_pct_at_entry,
index_regime_on,breadth_pct,
vcp_contractions,base_length_sessions,base_depth_pct,final_contraction_pct,depth_ratio,
pivot_vs_base_high_pct,entry_vs_pivot_pct,breakout_vol_ratio,stop_pct,
rs_rank,dist_52w_high_pct,sma50_slope_20d_pct,setup_score
```

`exit_reason` codes: `initial_stop`, `trail_swing_low`, `trail_step`, `sma50_close`, `time_stop`, `partial_target`, `kill_switch`, `period_end`.

Stock fields:
- `mcap_cr`: market cap at entry, ₹ crore, point-in-time
- `cap_bucket`: from mcap rank at entry (large = top 100, mid = 101–250, small = 251–500, micro = rest)
- `index_membership`: `NIFTY50` | `NEXT50` | `MIDCAP150` | `SMALLCAP250` | `none`, point-in-time
- `adv_20d_cr`: 20-day average traded value, ₹ crore
- `position_pct_adv`: entry value ÷ `adv_20d_cr`
- `prior_trades_symbol`, `prior_stopouts_symbol_90d`: re-entry history on that stock

## 3. equity.csv

```
date,equity,cash,position_value,invested_pct,open_positions,open_risk_pct,
drawdown_pct,ladder_level,index_regime_on,breadth_pct,benchmark_tri
```

## 4. refusals.csv

Same setup-feature columns as trades.csv, plus:

```
date,symbol,reason,would_be_entry,would_be_stop,fwd_r_20d,fwd_r_60d
```

`fwd_r_*`: R the trade would have reached using the same stop. This is how a risk gate's cost gets measured (e.g. the 316 industry-cap refusals in the hold-out).

## 5. signals.csv

Every setup that fired, before risk gates. Lets taken vs refused vs ignored be compared on the same features.

```
date,symbol,setup_score,taken,refusal_reason,trade_id,<all setup + stock feature columns>
```

## 6. stocks.csv

One row per symbol that produced at least one signal.

```
symbol,industry,cap_bucket_mode,signals,trades,wins,net_pnl,total_r,expectancy_r,
best_trade_r,worst_trade_r,stopouts,avg_hold_sessions,first_trade,last_trade
```

Used to answer: is S1 profitable across stocks, or carried by a few names? Which stocks repeatedly stop out?

---

## Rules
- Units: % as 0 to 100, R as a multiple, money in ₹ with no separators.
- Dates: ISO `YYYY-MM-DD`.
- Every number net of costs unless the field name says `gross`.
- Hold-out runs: `split = hold_out`, and each run is logged with the in-sample run it validates.
- Stock attributes (mcap, index membership, liquidity) are point-in-time, never today's values.
- Results page and analysis read only from these files.
