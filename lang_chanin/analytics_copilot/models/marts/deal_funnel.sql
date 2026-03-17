with deals as (
    select * from {{ ref('stg_deals') }}
)

select
    stage,
    count(deal_id)                          as deal_count,
    round(sum(deal_value)::numeric, 0)               as total_value,
    round(avg(deal_value)::numeric, 0)               as avg_deal_value,
    round(avg(probability)::numeric, 0)              as avg_probability,

    -- weighted pipeline (olasılığa göre ağırlıklı değer)
    round((sum(deal_value * probability / 100))::numeric, 0)   as weighted_value

from deals
group by 1
order by
    case stage
        when 'Prospecting'   then 1
        when 'Qualification' then 2
        when 'Proposal'      then 3
        when 'Negotiation'   then 4
        when 'Closed Won'    then 5
        when 'Closed Lost'   then 6
    end
