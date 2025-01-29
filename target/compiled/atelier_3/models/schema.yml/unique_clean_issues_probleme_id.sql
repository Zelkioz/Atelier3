
    
    

select
    probleme_id as unique_field,
    count(*) as n_records

from "nodejs_lake"."main_cleansed"."clean_issues"
where probleme_id is not null
group by probleme_id
having count(*) > 1


