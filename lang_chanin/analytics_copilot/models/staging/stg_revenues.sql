with source as (
    select * from raw.revenues
),

cleaned as (
    select
        revenue_id,
        deal_id,
        company_id,
        revenue_date::date               as revenue_date,
        amount,
        revenue_type,

        -- ay bazında gruplama için
        date_trunc('month', revenue_date::date)  as revenue_month

    from source
)

select * from cleaned
