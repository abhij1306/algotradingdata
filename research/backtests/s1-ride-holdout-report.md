# S1 ride top-3 on the hold-out (2026-10-28)

Owner request. `--rerun <in-sample run> --split hold_out --from 2022-01-01 --to 2026-10-25` (config unchanged,
enforced by discipline.check_hold_out). Log: s1-ride-holdout.log. Benchmark (NIFTY 500 TRI) CAGR 8.79%.

| variant | in-sample run | hold-out run | trades | win % | exp R | CAGR % | max DD % | MAR | invested % | open | CAGR ex top-5 % | top-5 share % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rs_r075_ratio09 (frozen) | 01a17e77 | 01a1805a-544f-76a5-9ee2-7eb8a3a790d8 | 220 | 24.5 | 0.104 | 1.54 | 33.06 | 0.05 | 47.6 | 3.81 | -7.99 | 531 |
| slot_rs | 01a17e12 | 01a18064-4c3b-7337-99f6-0770f65d2c46 | 166 | 27.1 | 0.148 | 2.71 | 25.41 | 0.11 | 49.5 | 3.00 | -8.33 | 349 |
| rs_r075 | 01a17e6c | 01a1806d-bc46-7638-905c-60f62b6d6f9c | 196 | 28.1 | 0.209 | 4.01 | 25.10 | 0.16 | 45.1 | 3.62 | -4.91 | 204 |

In-sample (2016-2021) for reference: exp R 0.688 / 0.665 / 0.619, CAGR 16.73 / 17.91 / 14.51, MAR 0.82 / 0.72 / 0.69.

By year return % (benchmark): 2022 -11.0/-10.4/-10.1 (4.2); 2023 60.0/55.6/53.6 (26.9);
2024 -16.0/-14.5/-7.1 (16.2); 2025 -7.0/-2.7/-3.1 (7.8); 2026 to 10-25 -3.3/-1.9/-2.9 (-9.5).
Longest drawdown in all three: 670 sessions from 2024-02-08, not recovered by 2026-10-23.

Reading: expectancy fell 70-85% out of sample; every variant trails the benchmark; all the profit is 2023.
The in-sample ranking reversed: the most-tuned variant (ratio09) is worst, the least-tuned of the three best.
The hold-out has now been used by s1-book-01 and these three; it can no longer select among them cleanly.
