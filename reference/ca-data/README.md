# NSE backtest data: rights, demergers, splits/bonus, board meetings, results announcements
Collected 24-Oct-2026. Window: 24-Oct-2011 to 23-Oct-2026 (rolling 15 years).
All data from free official NSE APIs behind nseindia.com (corporate actions, corporate
announcements, board meetings) plus one official NSE listing circular for ETF unit splits.
No login, no paid data. Zero failed chunks in any pull (each chunk retried up to 5x).

## Files (CSV windows: 5y = 2021-2026, then 2016_2021, 2011_2016)
- rights_issues_5y.csv (200) / rights_issues_2016_2021.csv (72) / rights_issues_2011_2016.csv (48):
  main-board EQ rights. subject_raw preserved; entitlement_ratio_parsed and premium_rs_parsed are
  parsed from subject text. faceVal separate; subscription price NOT independently verified.
  Non-simple entitlements kept raw (ZUARI 2019 CCDs; one 5y record with CCPS+warrants).
- rights_issues_sme_5y.csv (36): SME EMERGE rights. NOTE: NSE's SME corporate-actions feed has
  no records before 01-Aug-2017 and zero SME rights/demergers in the whole 2016-2021 window
  (708 records checked); SME coverage before Aug-2017 is a source gap.
- rights_issues_invit_5y.csv (4) / rights_issues_invit_2016_2021.csv (1): InvIT rights, NOT equity.
- demergers_5y.csv (67) / demergers_2016_2021.csv (56) / demergers_2011_2016.csv (53):
  demerger ex/record dates with ratios recovered from NSE announcement filings and audited
  against the correct event and direction (resulting-co shares per demerged-co share).
  status=found means a human-audited evidence quote + source URL is on the row; composite
  schemes keep legs in ratio_note. status=unresolved means the ratio was NOT found in the
  company's NSE announcement filings scanned around the event (record-date intimations and
  scheme-sanction letters); the full scheme-of-arrangement document was not inspected, so the
  ratio may still exist there. Counts: 5y 63/67 found; 2016-2021 32/56; 2011-2016 5/53.
  IDFC demerger: EQ ex-date 01-Oct-2015; 13 H-series rows with ex-date 29-Sep-2015 collapsed
  into the single EQ event (noted here, H-series rows kept only in raw work files).
- splits_bonus_2011_2016.csv (251) / splits_bonus_2016_2021.csv (248) / splits_bonus_2021_2026.csv (522):
  face-value splits and bonuses, subject_raw preserved. action_type is split / bonus / bonus+split for combined events (22 such records, e.g. BAJFINANCE 08-Sep-2016); the adjustment needs both legs. instrument_class:
  equity / preference / debentures / warrants / unknown, with classification_source
  (subject | announcement) and evidence text + URL. Splits are classified equity by definition
  (face-value split of the equity share). Plain "Bonus X:Y" subjects are classified only when
  announcement evidence exists, else left unknown - do not assume unknown means equity.
  Known non-equity cases caught: NTPC 20-Mar-2015 "Bonus Debentures 1:1", BLUEDART 17-Nov-2014
  bonus debentures, NTPC 19-Mar-2019 "Bonus 1:5" (debentures per Reg 57(1) filings),
  PCJEWELLER 2017, BRITANNIA 2019 + 2021 (bonus debentures), TVSMOTOR 25-Aug-2025 and
  TVSHLTD 08-Sep-2026 ("Scheme Of Arrangement - Bonus Ncrps", preference).
- etf_unit_actions_2011_2026.csv (6): ETF unit face-value splits are NOT in NSE's
  corporate-actions API (checked equities and etf indexes). These 6 come from official NSE
  circular NSE/CML/42873 (11-Dec-2019), effective 19-Dec-2019: NIFTYBEES/BANKBEES/PSUBNKBEES/
  NETFNV20/HNGSNGBEES FV 10->1, GOLDBEES FV 100->1. GOLDBEES record date 20-Dec-2019 per
  Nippon India MF corporate-action page. Other AMCs' ETF actions are not covered here.
- reference_events_outside_window.csv (1): TITAN Bonus 1:1 + FV split 10->1 ex 23-Jun-2011,
  before the window start; kept as a named reference, window not expanded.
  (NSE CA feed has data back to at least 2010 if deeper history is ever wanted.)
- board_meetings_5y/2016_2021/2011_2016.csv (85,456 / 42,849 / 36,926): board-meeting
  intimations, all purposes. meeting_date = scheduled meeting; intimation_time = when the
  exchange published the intimation.
- results_announcements_5y/2016_2021/2011_2016.csv (83,190 / 70,517 / 41,773): announcements
  whose category is financial-results or outcome-of-board-meeting (incl. clarification and
  delayed-submission variants), with announcement_dt and exchange_dissemination_dt as recorded.
- nse_corp_actions.db: SQLite with all of the above as tables (rights_issues, demergers,
  splits_bonus, board_meetings, results_announcements, etf_unit_actions,
  reference_events_outside_window), every row tagged with source_file. Row counts validated
  against the CSVs at build time (all OK).

## Date semantics (important for the backtest)
- exDate: first day the stock trades ex the entitlement (price adjusts here).
- recDate: record date for eligibility.
- Corporate-actions feed has NO announcement date - when-the-market-learned-it timestamps come
  from the announcements data (announcement_dt, exchange_dissemination_dt).
- Timestamps preserved exactly as NSE recorded them, including late-night entries; companies
  file revisions/corrections as separate later rows - no deduplication applied and no blanket
  point-in-time-safety claim. Filter/validate per your catalyst logic.

## Scope
- Equities = NSE main-board EQ series (+ separate SME/InvIT files where they exist).
  Bhavcopy not included (earlier collection was cancelled and deleted).
- Announcements-based files cover symbols as named at the time; renamed symbols keep old rows.
- Raw pull JSONs and work scripts are under /data/home/fc/nse_data/work/ for re-derivation.
