## Coverage by year and format

Parse outcomes: `/tmp/claude-1000/-data-workspace-wt-hat-s2-ep-results/a33e3310-a437-464e-9ec7-91e531adc7c9/scratchpad/filings-hat_live-scope.csv`, 18,728 rows (one per filing and basis candidate).

| year | format | found | stored | already/same | insurance | excluded |
| --- | --- | --- | --- | --- | --- | --- |
| 2020 | (unread) | 2 | 0 | 0 | 0 | 2 |
| 2020 | reg33_banking | 129 | 129 | 0 | 0 | 0 |
| 2020 | reg33_indas | 2048 | 2047 | 1 | 0 | 0 |
| 2020 | reg33_nbfc | 167 | 163 | 4 | 0 | 0 |
| 2021 | (unread) | 44 | 0 | 0 | 0 | 44 |
| 2021 | reg33_banking | 91 | 91 | 0 | 0 | 0 |
| 2021 | reg33_indas | 2127 | 2124 | 3 | 0 | 0 |
| 2021 | reg33_nbfc | 179 | 178 | 1 | 0 | 0 |
| 2022 | (unread) | 13 | 0 | 1 | 0 | 12 |
| 2022 | reg33_banking | 103 | 102 | 1 | 0 | 0 |
| 2022 | reg33_indas | 2144 | 2140 | 4 | 0 | 0 |
| 2022 | reg33_nbfc | 180 | 180 | 0 | 0 | 0 |
| 2023 | (unread) | 22 | 0 | 0 | 0 | 22 |
| 2023 | reg33_banking | 115 | 114 | 1 | 0 | 0 |
| 2023 | reg33_indas | 2316 | 2308 | 8 | 0 | 0 |
| 2023 | reg33_nbfc | 199 | 199 | 0 | 0 | 0 |
| 2024 | (unread) | 1 | 0 | 1 | 0 | 0 |
| 2024 | insurance_skipped | 22 | 0 | 0 | 22 | 0 |
| 2024 | integrated_indas | 3 | 2 | 0 | 0 | 1 |
| 2024 | reg33_banking | 136 | 136 | 0 | 0 | 0 |
| 2024 | reg33_indas | 2421 | 2394 | 27 | 0 | 0 |
| 2024 | reg33_nbfc | 213 | 210 | 3 | 0 | 0 |
| 2025 | (unread) | 72 | 0 | 71 | 0 | 1 |
| 2025 | insurance_skipped | 45 | 0 | 0 | 45 | 0 |
| 2025 | integrated_banking | 147 | 141 | 3 | 0 | 3 |
| 2025 | integrated_indas | 2767 | 2637 | 83 | 0 | 47 |
| 2025 | integrated_nbfc | 284 | 269 | 13 | 0 | 2 |
| 2025 | other | 7 | 7 | 0 | 0 | 0 |
| 2026 | (unread) | 73 | 0 | 73 | 0 | 0 |
| 2026 | insurance_skipped | 30 | 0 | 0 | 30 | 0 |
| 2026 | integrated_banking | 105 | 100 | 4 | 0 | 1 |
| 2026 | integrated_indas | 1605 | 1532 | 67 | 0 | 6 |
| 2026 | integrated_nbfc | 189 | 175 | 14 | 0 | 0 |
| 2026 | other | 3 | 3 | 0 | 0 | 0 |

Excluded, by reason:

| reason | count |
| --- | --- |
| xbrl_http_404 | 75 |
| q4_nine_month_missing | 60 |
| period_missing | 6 |

Secondary-source rows backfilled, by period-end year (DB):

| year | rows |
| --- | --- |
| 2020 | 7 |
| 2021 | 9 |
| 2022 | 14 |
| 2023 | 232 |
| 2024 | 339 |
| 2025 | 100 |
| 2026 | 25 |

## Counts

| count | rows | query |
| --- | --- | --- |
| rows | 18,204 | `select count(*) from hat_financial_result` |
| nse rows | 17,478 | `select count(*) from hat_financial_result where source='nse'` |
| secondary rows | 726 | `select count(*) from hat_financial_result where source='secondary'` |
| insurance_skipped rows | 97 | `select count(*) from hat_financial_result where format='insurance_skipped'` |
| instruments | 810 | `select count(distinct instrument_id) from hat_financial_result` |
| q4_derived | 51 | `select count(*) from hat_financial_result where q4_derived` |
| period_mismatch | 2 | `select count(*) from hat_financial_result where period_mismatch` |
| revisions (version > 1) | 103 | `select count(*) from hat_financial_result where version > 1` |
| public_at_estimated | 423 | `select count(*) from hat_financial_result where public_at_estimated` |
| unit_suspect (growth) | 40 | `select count(*) from hat_financial_growth where unit_suspect` |
| growth rows | 18,107 | `select count(*) from hat_financial_growth` |
| growth with sales_yoy | 14,167 | `select count(*) from hat_financial_growth where sales_yoy is not null` |
| growth with eps_yoy | 12,129 | `select count(*) from hat_financial_growth where eps_yoy is not null` |

| source | public_at_source | estimated | rows |
| --- | --- | --- | --- |
| nse | announcement | False | 15556 |
| nse | xbrl | False | 1904 |
| nse | xbrl_date | True | 18 |
| secondary | announcement | False | 321 |
| secondary | deadline | True | 405 |

## Secondary-source cross-check

Pairs (NSE quarter also on the secondary page, same basis): 8,772.

| field | basis | compared | mismatched (>1% and > Rs 0.5 cr / Rs 0.01) | rate |
| --- | --- | --- | --- | --- |
| revenue | consolidated | 8427 | 534 | 6.34% |
| revenue | standalone | 345 | 21 | 6.09% |
| revenue | all | 8772 | 555 | 6.33% |
| net_profit | consolidated | 8427 | 2682 | 31.83% |
| net_profit | standalone | 345 | 3 | 0.87% |
| net_profit | all | 8772 | 2685 | 30.61% |
| eps | consolidated | 8424 | 1730 | 20.54% |
| eps | standalone | 345 | 30 | 8.70% |
| eps | all | 8769 | 1760 | 20.07% |

Worst 20, revenue:

| symbol | period_end | basis | NSE | secondary | rel diff |
| --- | --- | --- | --- | --- | --- |
| RAJESHEXPO | 2026-06-30 | consolidated | 1,317.89 cr | 240,336.00 cr | 18136.4% |
| PFC | 2023-12-31 | consolidated | 235.72 cr | 23,572.00 cr | 9900.1% |
| NAVNETEDUL | 2026-03-31 | consolidated | 4.30 cr | 430.00 cr | 9900.0% |
| METROBRAND | 2025-09-30 | consolidated | 6.51 cr | 651.00 cr | 9897.8% |
| EMBDL | 2024-03-31 | consolidated | 21.02 cr | 380.00 cr | 1707.8% |
| PAYTM | 2023-09-30 | consolidated | 251.86 cr | 2,519.00 cr | 900.2% |
| ONESOURCE | 2024-09-30 | consolidated | 67.98 cr | 334.00 cr | 391.3% |
| SUDARSCHEM | 2025-03-31 | consolidated | -646.70 cr | 1,349.00 cr | 308.6% |
| SYMPHONY | 2025-03-31 | consolidated | -600.00 cr | 488.00 cr | 181.3% |
| WELCORP | 2025-03-31 | consolidated | -6,127.60 cr | 3,925.00 cr | 164.1% |
| COFORGE | 2025-03-31 | consolidated | -5,371.40 cr | 3,422.00 cr | 163.7% |
| CGPOWER | 2025-03-31 | consolidated | -4,403.12 cr | 2,753.00 cr | 162.5% |
| SHYAMMETL | 2025-03-31 | consolidated | -6,858.78 cr | 4,139.00 cr | 160.3% |
| BALKRISIND | 2025-03-31 | consolidated | -4,942.19 cr | 2,752.00 cr | 155.7% |
| ZEEL | 2025-03-31 | consolidated | -3,925.90 cr | 2,184.00 cr | 155.6% |
| PFIZER | 2025-03-31 | standalone | -1,097.53 cr | 592.00 cr | 153.9% |
| SANSERA | 2025-03-31 | consolidated | -1,453.45 cr | 782.00 cr | 153.8% |
| GVPIL | 2025-03-31 | consolidated | -514.34 cr | 266.00 cr | 151.7% |
| MANKIND | 2025-03-31 | consolidated | -6,120.56 cr | 3,079.00 cr | 150.3% |
| SYRMA | 2025-03-31 | consolidated | -1,937.47 cr | 924.00 cr | 147.7% |

Worst 20, net_profit:

| symbol | period_end | basis | NSE | secondary | rel diff |
| --- | --- | --- | --- | --- | --- |
| PRAJIND | 2025-12-31 | consolidated | -0.00 cr | -12.00 cr | 1199900.0% |
| PRAJIND | 2024-09-30 | consolidated | 0.01 cr | 54.00 cr | 650502.4% |
| RPOWER | 2024-09-30 | consolidated | -0.56 cr | 2,878.00 cr | 514028.6% |
| GLENMARK | 2026-03-31 | consolidated | -0.10 cr | 301.00 cr | 316942.1% |
| PVRINOX | 2024-06-30 | consolidated | 0.10 cr | -179.00 cr | 179100.0% |
| KAYNES | 2024-09-30 | consolidated | 0.12 cr | 60.00 cr | 51624.1% |
| PRIVISCL | 2024-06-30 | consolidated | -0.06 cr | 31.00 cr | 49463.1% |
| DEVYANI | 2024-09-30 | consolidated | 0.02 cr | -5.00 cr | 29511.8% |
| SHYAMMETL | 2025-09-30 | consolidated | -1.31 cr | 260.00 cr | 19947.3% |
| PFC | 2023-12-31 | consolidated | 47.68 cr | 6,294.00 cr | 13101.2% |
| WAAREEENER | 2025-12-31 | consolidated | 9.52 cr | 1,107.00 cr | 11528.2% |
| NAVNETEDUL | 2026-03-31 | consolidated | 0.38 cr | 39.00 cr | 10163.2% |
| METROBRAND | 2025-09-30 | consolidated | 0.68 cr | 69.00 cr | 10093.5% |
| KIRLOSBROS | 2025-06-30 | consolidated | 0.80 cr | 68.00 cr | 8400.0% |
| ADANIPORTS | 2025-06-30 | consolidated | 52.67 cr | 3,311.00 cr | 6186.3% |
| STAR | 2024-06-30 | consolidated | 70.20 cr | 3,350.00 cr | 4671.9% |
| FRETAIL | 2020-03-31 | consolidated | 11.57 cr | -478.00 cr | 4230.3% |
| SOLARINDS | 2024-09-30 | consolidated | 7.76 cr | 304.00 cr | 3817.5% |
| CARERATING | 2023-06-30 | consolidated | 0.55 cr | 18.00 cr | 3198.5% |
| JBCHEPHARM | 2024-03-31 | consolidated | -4.24 cr | 126.00 cr | 3071.7% |

Worst 20, eps:

| symbol | period_end | basis | NSE | secondary | rel diff |
| --- | --- | --- | --- | --- | --- |
| STAR | 2024-06-30 | consolidated | 7.64 | 364.69 | 4673.4% |
| FRETAIL | 2020-03-31 | consolidated | 0.23 | -9.09 | 4052.2% |
| SWIGGY | 2024-09-30 | consolidated | -2.80 | -62.75 | 2141.1% |
| TMPV | 2025-09-30 | consolidated | -17.50 | 206.85 | 1282.0% |
| VIYASH | 2024-12-31 | consolidated | 0.14 | 1.78 | 1171.4% |
| ADANIENT | 2024-12-31 | consolidated | 0.04 | 0.45 | 1025.0% |
| SWANCORP | 2025-12-31 | consolidated | -0.04 | -0.31 | 675.0% |
| EMBDL | 2024-06-30 | consolidated | -0.49 | 1.93 | 493.9% |
| PFIZER | 2025-03-31 | standalone | -23.10 | 72.34 | 413.2% |
| ALLCARGO | 2025-09-30 | consolidated | -0.03 | 0.09 | 400.0% |
| TRIVENI | 2025-06-30 | consolidated | 0.02 | 0.10 | 400.0% |
| ALLCARGO | 2025-03-31 | consolidated | -0.12 | 0.25 | 308.3% |
| TITAGARH | 2025-03-31 | consolidated | 4.79 | -9.09 | 289.8% |
| RAJESHEXPO | 2026-06-30 | consolidated | 0.42 | 1.60 | 281.0% |
| VIYASH | 2025-09-30 | consolidated | 0.59 | 2.18 | 269.5% |
| SYRMA | 2025-03-31 | consolidated | -2.20 | 3.67 | 266.8% |
| EMBDL | 2024-09-30 | consolidated | 0.38 | -0.54 | 242.1% |
| SYMPHONY | 2025-03-31 | consolidated | -8.11 | 11.50 | 241.8% |
| WELCORP | 2025-03-31 | consolidated | -19.53 | 26.62 | 236.3% |
| RAJESHEXPO | 2024-03-31 | consolidated | 1.02 | -1.03 | 201.0% |

