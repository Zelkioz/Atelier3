
  
    
    

    create  table
      "nodejs_lake"."main_cleansed"."clean_issues__dbt_tmp"
  
    as (
      

with problemes_bruts as (

    select * from "nodejs_lake"."raw"."issues"

),

problemes_nettoyes as (

    select
        id as probleme_id,
        trim(title) as titre,  -- Supprime les espaces en début et fin
        nullif(trim(body), '') as description,  -- Convertit les chaînes vides en null
        cast(created_at as timestamp) as date_creation,  -- Assure un format timestamp cohérent
        cast(updated_at as timestamp) as date_modification,  -- Assure un format timestamp cohérent
        lower(state) as etat,  -- Normalise l'état en minuscules
        user_id as id_contributeur
    from problemes_bruts
    where id is not null  -- Garde uniquement les enregistrements valides
      and title is not null  -- Le titre est requis
      and user_id is not null  -- Doit avoir un créateur valide
      and lower(state) = 'open'  -- Garde uniquement les problèmes ouverts, insensible à la casse
)

select * from problemes_nettoyes
    );
  
  