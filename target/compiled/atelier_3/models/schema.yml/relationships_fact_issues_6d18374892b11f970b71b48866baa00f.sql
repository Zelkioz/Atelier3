
    
    

with child as (
    select contributor_id as from_field
    from "nodejs_lake"."main_application"."fact_issues"
    where contributor_id is not null
),

parent as (
    select contributeur_id as to_field
    from "nodejs_lake"."main_application"."dim_contributor"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


