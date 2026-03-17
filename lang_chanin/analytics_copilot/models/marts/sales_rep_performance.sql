with deals as (
    select * from {{ ref('stg_deals') }}
)

select
    owner                                                               as sales_rep,
    count(deal_id)                                                      as total_deals,
    round(sum(deal_value)::numeric, 0)                                           as total_pipeline,
    round(sum(case when is_won then deal_value end)::numeric, 0)                 as total_won_revenue,
    count(case when is_won then 1 end)                                  as won_deals,
    count(case when stage = 'Closed Lost' then 1 end)                   as lost_deals,
    round(avg(case when is_won then days_to_close end)::numeric, 0)              as avg_days_to_close,

    -- win rate
    round(
        count(case when is_won then 1 end)::numeric /
        nullif(
            count(case when stage in ('Closed Won','Closed Lost') then 1 end)
        , 0) * 100
    , 1)                                                                as win_rate_pct

from deals
group by 1
order by total_won_revenue desc nulls last
