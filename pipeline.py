import os
import requests
import json
import time
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
from datetime import datetime
import logging

# Configuration initiale
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
import json
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
from dotenv import load_dotenv

def fetch_all_pages(url, headers=None, params=None):
    """
    Récupère toutes les pages de résultats depuis l'API GitHub,
    en gérant automatiquement la pagination jusqu'à ce qu'il n'y ait plus de pages.
    """
    if headers is None:
        headers = {}
    if params is None:
        params = {}
        
    # Configuration sécurité
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Le token GitHub est manquant dans le fichier .env")
    headers["Authorization"] = f"token {token}"
    
    results = []
    retries = 3
    wait_time = 60
    
    page_count = 0
    while url and page_count < 100 and len(results) < 20000:
        for attempt in range(retries):
            try:
                logging.info(f"Tentative de récupération {url} (essai {attempt+1}/{retries})")
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                # Vérifier les limites de l'API
                if int(response.headers.get('X-RateLimit-Remaining', 0)) < 10:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 300))
                    sleep_duration = max(reset_time - time.time(), 60)
                    logging.warning(f"Limite API atteinte - Pause de {sleep_duration}s")
                    time.sleep(sleep_duration)
                
                response.raise_for_status()

                # Traitement de la réponse
                page_data = response.json()

                if isinstance(page_data, list):
                    results.extend(page_data)
                else:
                    results.append(page_data)

                # Gestion de la pagination
                page_count += 1
                if page_count >= 100:
                    logging.info("Limite de 100 pages atteinte.")
                    url = None
                elif 'Link' in response.headers:
                    links = parse_link_header(response.headers['Link'])
                    url = links.get('next')
                else:
                    url = None

                if params.get('page'):
                    params['page'] += 1

                break  # Sortir de la boucle de retry après succès

            except requests.exceptions.RequestException as e:
                logging.error(f"Erreur lors de la requête : {str(e)}")
                if attempt == retries - 1:
                    raise RuntimeError(f"Échec après {retries} tentatives") from e
                logging.info(f"Nouvel essai dans {wait_time} secondes...")
                time.sleep(wait_time)
            except KeyboardInterrupt:
                logging.warning("Interruption par l'utilisateur détectée. Arrêt du programme.")
                return results
        if isinstance(page_data, list):
            results.extend(page_data)
        else:
            # Si la réponse n'est pas une liste (par exemple, un dict), ajuster en conséquence
            results.append(page_data)
        # Gérer la présence d'un lien "next"
        if 'Link' in response.headers:
            links = parse_link_header(response.headers['Link'])
            url = links.get('next')
        else:
            url = None  # No more pages
        # Increment page parameter if needed
        if params.get('page'):
            params['page'] += 1
    return results

def parse_link_header(link_header):
    """
    Analyse le header Link de GitHub pour extraire les URL de next, prev, last, etc.
    Exemple d'un header Link :
    <https://api.github.com/resource?page=2>; rel="next",
    <https://api.github.com/resource?page=5>; rel="last"
    """
    links = {}
    for part in link_header.split(','):
        section = part.split(';')
        if len(section) < 2:
            continue
        url = section[0].strip().lstrip('<').rstrip('>')
        name = section[1].strip().split('=')[1].strip('"')
        links[name] = url
    return links

def convert_json_to_parquet(json_file, parquet_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 'data' doit être une liste de dictionnaires
    table = pa.Table.from_pylist(data)
    pq.write_table(table, parquet_file)
    print(f"{parquet_file} généré avec succès.")

def main():
    load_dotenv()  # Charger les variables d'environnement depuis le fichier .env
    token = os.getenv("GITHUB_TOKEN")  # Obtenir le token depuis la variable d'environnement
    if not token:
        raise Exception("Veuillez définir la variable d'environnement GITHUB_TOKEN.")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Créer une connexion DuckDB
    con = duckdb.connect("nodejs_lake.duckdb")

    # Récupérer et traiter les Contributors
    base_contributors_url = "https://api.github.com/repos/nodejs/node/contributors"
    params_contributors = {"per_page": 100}
    print("Récupération des contributors...")
    all_contributors = fetch_all_pages(base_contributors_url, headers=headers, params=params_contributors)
    
    # Pour chaque contributeur, récupérer ses informations détaillées
    detailed_contributors = []
    for contributor in all_contributors:
        user_url = contributor['url']
        user_details = fetch_all_pages(user_url, headers=headers)
        if isinstance(user_details, list) and len(user_details) > 0:
            detailed_contributors.append(user_details[0])
        else:
            detailed_contributors.append(user_details)
    
    with open("data/contributors_raw.json", "w", encoding="utf-8") as f:
        json.dump(detailed_contributors, f, indent=2, ensure_ascii=False)
    print(f"{len(detailed_contributors)} contributors récupérés.")
    convert_json_to_parquet("data/contributors_raw.json", "data/contributors.parquet")
    # Charger dans DuckDB
    con.execute("DROP TABLE IF EXISTS raw_contributors;")
    con.execute("CREATE TABLE raw_contributors AS SELECT * FROM 'data/contributors.parquet';")
    result = con.execute("SELECT COUNT(*) FROM raw_contributors;").fetchone()
    print(f"Nombre de lignes dans raw_contributors : {result[0]}")

    # Récupérer et traiter les Issues
    base_issues_url = "https://api.github.com/repos/nodejs/node/issues"
    params_issues = {"state": "all", "per_page": 100}
    print("Récupération des issues...")
    all_issues = fetch_all_pages(base_issues_url, headers=headers, params=params_issues)
    os.makedirs("data", exist_ok=True)
    with open("data/issues_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_issues, f, indent=2, ensure_ascii=False)
    print(f"{len(all_issues)} issues récupérées.")
    convert_json_to_parquet("data/issues_raw.json", "data/issues.parquet")
    # Charger dans DuckDB
    con.execute("DROP TABLE IF EXISTS raw_issues;")
    con.execute("CREATE TABLE raw_issues AS SELECT * FROM 'data/issues.parquet';")
    result = con.execute("SELECT COUNT(*) FROM raw_issues;").fetchone()
    print(f"Nombre de lignes dans raw_issues : {result[0]}")

    # Récupérer et traiter les Pull Requests
    base_pulls_url = "https://api.github.com/repos/nodejs/node/pulls"
    params_pulls = {"state": "all", "per_page": 100}
    print("Récupération des pull requests...")
    all_pulls = fetch_all_pages(base_pulls_url, headers=headers, params=params_pulls)
    with open("data/pulls_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_pulls, f, indent=2, ensure_ascii=False)
    print(f"{len(all_pulls)} pull requests récupérées.")
    convert_json_to_parquet("data/pulls_raw.json", "data/pulls.parquet")
    # Charger dans DuckDB
    con.execute("DROP TABLE IF EXISTS raw_pull_requests;")
    con.execute("CREATE TABLE raw_pull_requests AS SELECT * FROM 'data/pulls.parquet';")
    result = con.execute("SELECT COUNT(*) FROM raw_pull_requests;").fetchone()
    print(f"Nombre de lignes dans raw_pull_requests : {result[0]}")

    # Récupérer et traiter les Commits
    base_commits_url = "https://api.github.com/repos/nodejs/node/commits"
    params_commits = {"per_page": 100}
    print("Récupération des commits...")
    all_commits = fetch_all_pages(base_commits_url, headers=headers, params=params_commits)
    with open("data/commits_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_commits, f, indent=2, ensure_ascii=False)
    print(f"{len(all_commits)} commits récupérés.")
    convert_json_to_parquet("data/commits_raw.json", "data/commits.parquet")
    # Charger dans DuckDB
    con.execute("DROP TABLE IF EXISTS raw_commits;")
    con.execute("CREATE TABLE raw_commits AS SELECT * FROM 'data/commits.parquet';")
    result = con.execute("SELECT COUNT(*) FROM raw_commits;").fetchone()
    print(f"Nombre de lignes dans raw_commits : {result[0]}")

    # Récupérer et traiter les Releases
    base_releases_url = "https://api.github.com/repos/nodejs/node/releases"
    params_releases = {"per_page": 100}
    print("Récupération des releases...")
    all_releases = fetch_all_pages(base_releases_url, headers=headers, params=params_releases)
    with open("data/releases_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_releases, f, indent=2, ensure_ascii=False)
    print(f"{len(all_releases)} releases récupérées.")
    convert_json_to_parquet("data/releases_raw.json", "data/releases.parquet")
    # Charger dans DuckDB
    con.execute("DROP TABLE IF EXISTS raw_releases;")
    con.execute("CREATE TABLE raw_releases AS SELECT * FROM 'data/releases.parquet';")
    result = con.execute("SELECT COUNT(*) FROM raw_releases;").fetchone()
    print(f"Nombre de lignes dans raw_releases : {result[0]}")

    # Fermer la connexion DuckDB
    con.close()
    print("Ingestion des données terminée avec succès.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Une erreur s'est produite : {e}")
