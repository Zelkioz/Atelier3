
    
    

select
    contributor_id as unique_field,
    count(*) as n_records

from "nodejs_lake"."main_application"."dim_contributor"
where contributor_id is not null
group by contributor_id
having count(*) > 1


