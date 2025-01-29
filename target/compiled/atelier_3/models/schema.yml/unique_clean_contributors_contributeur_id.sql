
    
    

select
    contributeur_id as unique_field,
    count(*) as n_records

from "nodejs_lake"."main_cleansed"."clean_contributors"
where contributeur_id is not null
group by contributeur_id
having count(*) > 1


