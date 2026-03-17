with source as (
    select * from raw.deals
),

cleaned as (
    select
        deal_id,
        company_id,
        contact_id,
        deal_name,
        stage,
        deal_value,
        probability,
        size_segment,
        owner,
        lost_reason,
        created_at::date                        as created_date,
        closed_at::date                         as closed_date,

        -- kaç günde kapandı
        case
            when closed_at is not null
            then closed_at::date - created_at::date
        end                                     as days_to_close,

        -- kazanıldı mı kaybedildi mi
        case
            when stage = 'Closed Won'  then true
            when stage = 'Closed Lost' then false
            else null
        end                                     as is_won

    from source
)

select * from cleaned
