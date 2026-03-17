with source as (
    select * from raw.contacts
),

cleaned as (
    select
        contact_id,
        company_id,
        first_name,
        last_name,
        first_name || ' ' || last_name   as full_name,
        title,
        email,
        created_at::date                 as created_date
    from source
)

select * from cleaned
