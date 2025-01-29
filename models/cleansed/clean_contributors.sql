{{ config(materialized='table', schema='cleansed') }}

with contributeurs_bruts as (

    select * from {{ source('raw', 'contributors') }}

),

contributeurs_nettoyes as (

    select
        id as contributeur_id,
        login as identifiant,
        coalesce(name, login) as nom,  -- Utilise l'identifiant comme nom si le nom est null
        nullif(trim(company), '') as entreprise,  -- Convertit les chaînes vides en null
        nullif(trim(location), '') as localisation,  -- Convertit les chaînes vides en null
        nullif(trim(email), '') as courriel,  -- Convertit les chaînes vides en null
        cast(created_at as timestamp) as date_creation,  -- Assure un format timestamp cohérent
        cast(updated_at as timestamp) as date_modification  -- Assure un format timestamp cohérent
    from contributeurs_bruts
    where id is not null  -- Garde uniquement les enregistrements valides
      and login is not null  -- L'identifiant est requis pour les contributeurs valides
)

select * from contributeurs_nettoyes
