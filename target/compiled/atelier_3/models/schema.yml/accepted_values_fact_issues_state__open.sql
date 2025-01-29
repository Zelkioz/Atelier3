
    
    

with all_values as (

    select
        state as value_field,
        count(*) as n_records

    from "nodejs_lake"."main_application"."fact_issues"
    group by state

)

select *
from all_values
where value_field not in (
    'open'
)


