with source as (
    select * from raw.companies
),

cleaned as (
    select
        company_id,
        company_name,
        industry,
        size_segment,
        country,
        created_at::date as created_date
    from source
)

select * from cleaned
