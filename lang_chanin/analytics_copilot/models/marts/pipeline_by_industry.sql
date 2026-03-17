with deals as (
    select * from {{ ref('stg_deals') }}
),

companies as (
    select * from {{ ref('stg_companies') }}
),

joined as (
    select
        c.industry,
        c.size_segment,
        count(d.deal_id)                                                as total_deals,
        round(sum(d.deal_value)::numeric, 0)                                     as total_pipeline_value,
        round(sum(case when d.is_won then d.deal_value end)::numeric, 0)         as won_revenue,
        count(case when d.is_won then 1 end)                            as won_deals,
        count(case when d.stage = 'Closed Lost' then 1 end)             as lost_deals,

        -- win rate
        round(
            count(case when d.is_won then 1 end)::numeric /
            nullif(
                count(case when d.stage in ('Closed Won','Closed Lost') then 1 end)
            , 0) * 100
        , 1)                                                            as win_rate_pct,

        -- ortalama deal değeri
        round(avg(d.deal_value)::numeric, 0)                            as avg_deal_value,

        -- ortalama kapanma süresi
        round(avg(d.days_to_close)::numeric, 0)                         as avg_days_to_close

    from deals d
    left join companies c using (company_id)
    group by 1, 2
)

select * from joined
order by total_pipeline_value desc
