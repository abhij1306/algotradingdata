# Backtest data coverage: NIFTY 500 point-in-time (2026-10-29)

Read-only checks over `HAT_DATA_ROOT=/data/workspace/hat-data-isin` and `hat_live`, after the Kotak 5m re-download and import (import done 2026-10-29 03:57 UTC), the ETF store rebuild, and the daily update (#309) that filled the 2026-10-28 5m bars.

| Series | Coverage | Gaps |
|---|---|---|
| Daily bars | 2011-06-22..2026-10-28 (features through 10-28) | 66 member-sessions since 2016 (REITs EMBASSY/BIRET, RELINFRA 22, …) |
| Index membership | 2016-01-01..2026-10-28 | Changes announced 10-23 and 10-28 take effect 10-30: rebuild after that |
| 5-minute bars | 2021-10-29..2026-10-28: **94.89%** of member-days with a daily bar (588,415 of 620,122; was 92.9%). By year: 2022 92.0%, 2023 94.9%, 2024 94.7%, 2025 96.4%, 2026 97.6% | 17,618 `basis_mismatch` days (was 28,154); 14,945 missing days with no reject recorded (was 16,045); 38,373 days with fewer than 75 bars; 26 members never have 5m (JBCHEPHARM, GSPL, ISEC, PEL, …); 21 of 272 former members had no Kotak data |
| 5m gap-day bias (2022+) | Days with no 5m: gap ≥ +6% **22.4%** (was 39.7%), gap ≤ −6% **24.7%** (was 50.7%), \|gap\| < 3% 4.8% | Median close-vs-open on gap-up days: −2.15% for days without 5m, −2.01% for days with it (was −3.36% vs −0.80%). The bias in EP results on the 5m basis is now small, but not zero |
| Results filings | As of the 10-28 fetch: quarters 2020-03..2026-09 (partial, 251 instruments); derived for 810 instruments, 18,080 rows | 0 new documents in the 10-28 fetch because the listings were still cached (20h) |
| index_daily | Through 10-28 | No NIFTY 50 TRI or 1D Rate Index there; both are only in the ETF store |
| ETF store (`HAT_DATA_ROOT/etf/`) | Daily NIFTYBEES/GOLDBEES/LIQUIDBEES, NIFTY 50, NIFTY 50 TRI and NIFTY 500 TRI: 2015-01-01..2026-10-28. 5m: 1,229 days each, 2021-11-01..2026-10-28. Dividends through 10-28 | 5m starts at Kotak's earliest date (2021-10-30). `etf_data.load` verifies the file checksums and loads in 2.4 s |

5m import, 2026-10-29: members 11,194 new days (827,544 bars), 521,503 kept as stored, 14,556 rejected `basis_mismatch`; former members 5,828 new days (427,605 bars), 227,634 kept, 12,325 `basis_mismatch` and 107 `no_daily_bar` rejected. Logs: `/data/workspace/hat-data-isin/logs/infra-2026-10-28/`.
