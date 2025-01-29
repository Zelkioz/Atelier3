
    
    

with all_values as (

    select
        etat as value_field,
        count(*) as n_records

    from "nodejs_lake"."main_cleansed"."clean_issues"
    group by etat

)

select *
from all_values
where value_field not in (
    'open'
)


