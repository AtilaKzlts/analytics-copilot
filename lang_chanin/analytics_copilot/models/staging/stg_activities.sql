with source as (
    select * from raw.activities
),

cleaned as (
    select
        activity_id,
        deal_id,
        activity_type,
        activity_date::date              as activity_date,
        duration_minutes,
        outcome,
        notes,

        -- olumlu mu olumsuz mu
        case
            when outcome = 'Positive' then true
            else false
        end                              as is_positive_outcome

    from source
)

select * from cleaned
