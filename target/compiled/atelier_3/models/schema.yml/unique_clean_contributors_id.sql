
    
    

select
    id as unique_field,
    count(*) as n_records

from "nodejs_lake"."main_cleansed"."clean_contributors"
where id is not null
group by id
having count(*) > 1


