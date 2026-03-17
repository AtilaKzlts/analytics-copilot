with revenues as (
    select * from {{ ref('stg_revenues') }}
),

monthly as (
    select
        revenue_month,
        revenue_type,
        count(distinct company_id)              as active_companies,
        count(distinct deal_id)                 as active_deals,
        round(sum(amount)::numeric, 0)                   as total_revenue,
        round(avg(amount)::numeric, 0)                   as avg_revenue_per_deal

    from revenues
    group by 1, 2
),

with_growth as (
    select
        *,
        lag(total_revenue) over (
            partition by revenue_type
            order by revenue_month
        )                                       as prev_month_revenue,

        round(
            (total_revenue - lag(total_revenue) over (
                partition by revenue_type order by revenue_month
            )) /
            nullif(lag(total_revenue) over (
                partition by revenue_type order by revenue_month
            ), 0) * 100
        , 1)                                    as mom_growth_pct

    from monthly
)

select * from with_growth
order by revenue_month desc
