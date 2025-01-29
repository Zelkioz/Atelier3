{{ config(materialized='table', schema='application') }}

select
    i.probleme_id as issue_id,
    i.titre as title,
    i.description as body,
    i.date_creation as created_at,
    i.date_modification as updated_at,
    i.etat as state,
    i.id_contributeur as contributor_id,
    c.login as contributor_login,
    -- Calcul des métriques temporelles
    datediff('hour', i.date_creation, i.date_modification) as heures_depuis_creation,
    case 
        when i.date_modification = i.date_creation then 'nouveau'
        else 'mis à jour'
    end as statut_mise_a_jour
from {{ ref('clean_issues') }} i
inner join {{ ref('dim_contributor') }} c  -- Utilise inner join pour assurer que nous n'avons que des problèmes avec des contributeurs valides
    on i.id_contributeur = c.contributeur_id
