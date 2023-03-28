with loan_level_summary as (
    select
        loan_id,
        substr(orig_date, 3, 4) as orig_year,
        orig_date,
        purpose,
        date_from_parts(right(orig_date,4), left(orig_date, length(orig_date) - 4), 1) as orig_dated,
        date_from_parts(right(a.act_period,4), left(a.act_period, length(a.act_period) - 4), 1) as first_period,
        date_from_parts(year(orig_dated), quarter(orig_dated) * 3, 1) as orig_quarter,
        orig_upb
    from fnma a
    where first_period = (
        select min(date_from_parts(right(b.act_period,4), left(b.act_period, length(b.act_period) - 4), 1))
        from fnma b
        where a.loan_id = b.loan_id
    )
)

select orig_year, orig_dated, orig_quarter, count(*) as orig_loan_count, sum(orig_upb) as orig_upb
from loan_level_summary
group by orig_year, orig_dated, orig_quarter