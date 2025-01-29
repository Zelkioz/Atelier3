
    
    

with child as (
    select id_contributeur as from_field
    from "nodejs_lake"."main_cleansed"."clean_issues"
    where id_contributeur is not null
),

parent as (
    select contributeur_id as to_field
    from "nodejs_lake"."main_cleansed"."clean_contributors"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


