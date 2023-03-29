select
    right(orig_date, 4) as orig_year,
    seller,
    date_from_parts(right(orig_date,4), left(orig_date, length(orig_date) - 4), 1) as orig_dated,
    date_from_parts(right(act_period,4), left(act_period, length(act_period) - 4), 1) as repurchase_periodd,
    MONTHS_BETWEEN(repurchase_periodd, orig_dated) as loan_age,
    date_from_parts(year(orig_dated),         quarter(orig_dated) * 3, 1)         as orig_quarter,
    date_from_parts(year(repurchase_periodd), quarter(repurchase_periodd) * 3, 1) as repurchase_quarter,
    MONTHS_BETWEEN(repurchase_quarter, orig_quarter) / 3 as loan_age_qtr,
    count(*) as loan_count,
    sum(last_upb) as repurchase_upb,
    sum(orig_upb) as orig_upb_at_terminal
from fnma
where zero_bal_code = '06'
group by orig_year, seller, repurchase_periodd, orig_dated, loan_age, orig_quarter, repurchase_quarter