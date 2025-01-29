

select
    contributeur_id,
    identifiant as login,
    nom as name,
    entreprise as company,
    localisation as location,
    courriel as email,
    date_creation as created_at,
    date_modification as updated_at
from "nodejs_lake"."main_cleansed"."clean_contributors"