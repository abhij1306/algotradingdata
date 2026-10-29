-- A4 rebuild verification on hat_live (read-only)
select 'rows', count(*) from hat_financial_result
union all select 'rows nse', count(*) from hat_financial_result where source='nse'
union all select 'rows secondary', count(*) from hat_financial_result where source='secondary'
union all select 'rows insurance_skipped', count(*) from hat_financial_result where format='insurance_skipped'
union all select 'growth rows', count(*) from hat_financial_growth
union all select 'q4_derived', count(*) from hat_financial_result where q4_derived
union all select 'q4_derived with negative revenue', count(*) from hat_financial_result where q4_derived and revenue < 0
union all select 'any quarter with negative revenue', count(*) from hat_financial_result where revenue < 0
union all select 'flag quarter_start_mislabelled', count(*) from hat_financial_result where quality_flags like '%quarter_start_mislabelled%'
union all select 'flag owners_profit_tag_swapped', count(*) from hat_financial_result where quality_flags like '%owners_profit_tag_swapped%'
union all select 'period_mismatch rows', count(*) from hat_financial_result where period_mismatch
union all select 'version > 1', count(*) from hat_financial_result where version > 1
union all select 'D2 AARTIDRUGS/MMTC 2024-06-30 rows', count(*) from hat_financial_result where symbol in ('AARTIDRUGS','MMTC') and period_end='2024-06-30'
union all select 'D2 AARTIDRUGS/MMTC 2024-06-30 version>1', count(*) from hat_financial_result where symbol in ('AARTIDRUGS','MMTC') and period_end='2024-06-30' and version > 1
union all select 'D2 rows from the misdated documents', count(*) from hat_financial_result where source_url like '%INTEGRATED_FILING_INDAS_1487066_18072025063655_WEB.xml' or source_url like '%INTEGRATED_FILING_INDAS_1505025_07082025033407_WEB.xml';
select 'period_mismatch', symbol, period_end, listing_period_end, version from hat_financial_result where period_mismatch order by 2,3;
