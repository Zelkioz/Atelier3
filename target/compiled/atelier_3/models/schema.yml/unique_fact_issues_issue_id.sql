
    
    

select
    issue_id as unique_field,
    count(*) as n_records

from "nodejs_lake"."main_application"."fact_issues"
where issue_id is not null
group by issue_id
having count(*) > 1


