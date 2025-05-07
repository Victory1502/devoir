import requests
import json
import time
from typing import List, Dict, Any, Optional
import os

# Configuration de l'API
BASE_URL = "https://projects.propublica.org/nonprofits/api/v2/search.json"
QUERY_PARAMS = {"q": "chat"}
OUTPUT_FILE = "c:/Users/dimbo/Documents/Master 1 data ingenieur/Solution d'échange inter-applicatif/exos2/exo2/associations_chat.json"

# Fonction pour extraire les données d'une page
def extract(page: int) -> Optional[Dict[str, Any]]:
    """
    Extrait les données d'une page spécifique de l'API.
    
    Args:
        page: Numéro de la page à extraire
        
    Returns:
        Dictionnaire contenant les données de la page ou None en cas d'erreur
    """
    try:
        # Construire les paramètres de requête
        params = QUERY_PARAMS.copy()
        params["page"] = page
        
        # Envoyer la requête à l'API
        print(f"Récupération de la page {page}...")
        response = requests.get(BASE_URL, params=params)
        
        # Vérifier le code de statut
        if response.status_code != 200:
            print(f"Erreur lors de la récupération de la page {page}: Code {response.status_code}")
            return None
        
        # Convertir la réponse en JSON
        data = response.json()
        
        # Vérifier si la page a des résultats
        if not data.get("organizations", []):
            print(f"Plus de résultats à la page {page}")
            return None
        
        # Afficher un aperçu pour le débogage
        print(f"Page {page}: {len(data.get('organizations', []))} organisations trouvées")
        
        return data
    
    except requests.RequestException as e:
        print(f"Erreur de requête pour la page {page}: {str(e)}")
        return None
    
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON pour la page {page}")
        return None
    
    except Exception as e:
        print(f"Erreur inattendue pour la page {page}: {str(e)}")
        return None


# Fonction pour transformer les données
def transform(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filtre et transforme les données extraites.
    
    Args:
        data: Dictionnaire contenant les données à transformer
        
    Returns:
        Liste des organisations filtrées et transformées
    """
    organizations = data.get("organizations", [])
    
    # Avant de filtrer, afficher un exemple d'organisation pour débogage
    if organizations:
        print(f"  Exemple de champs disponibles: {list(organizations[0].keys())}")
    
    # Filtrer les organisations (critères relâchés)
    filtered_orgs = []
    for org in organizations:
        # Nous gardons toutes les organisations, sans filtre
        # Ou avec un filtre très simple comme:
        # if org.get("name"):  # Si l'organisation a au moins un nom
        
        # Simplifier l'objet pour ne garder que les champs pertinents
        simplified_org = {
            "name": org.get("name", "Nom inconnu"),
            "city": org.get("city", "Ville inconnue"),
            "state": org.get("state", "État inconnu"),
            "income_amount": org.get("income_amount", 0),
            "ntee_code": org.get("ntee_code"),
            "ein": org.get("ein")
        }
        
        filtered_orgs.append(simplified_org)
    
    # Afficher le nombre d'organisations filtrées pour le débogage
    print(f"  → {len(filtered_orgs)} organisations retenues après filtrage")
    
    return filtered_orgs

# Fonction pour charger les données dans un fichier
def load(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Enregistre les données dans un fichier JSON.
    
    Args:
        data: Liste des données à enregistrer
        filename: Nom du fichier de sortie
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        # Afficher le chemin absolu
        import os
        print(f"Les données ont été enregistrées dans: {os.path.abspath(filename)}")
        
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des données: {str(e)}")
        print(f"Tentative d'enregistrement dans: {filename}")

# Fonction principale
def main():
    toutes_donnees = []
    page = 0
    total_revenus = 0
    nombre_organisations = 0
    max_pages = 110  # Limiter le nombre de pages pour éviter une boucle infinie
    
    # Boucle pour récupérer toutes les pages
    while page < max_pages:
        # Essayer jusqu'à 3 fois en cas d'échec
        for attempt in range(3):
            try:
                # Extraire les données
                data = extract(page)
                
                # Si pas de données, sortir de la boucle
                if data is None:
                    break
                
                # Transformer les données
                filtered_orgs = transform(data)
                
                # Ajouter les données filtrées à la liste principale
                toutes_donnees.extend(filtered_orgs)
                
                # Calculer les statistiques
                for org in filtered_orgs:
                    total_revenus += org.get("income_amount", 0)
                    nombre_organisations += 1
                
                # Passer à la page suivante
                page += 1
                
                # Pause pour éviter de surcharger l'API
                time.sleep(1)
                
                # Sortir de la boucle de tentatives
                break
                
            except Exception as e:
                print(f"Tentative {attempt + 1} échouée: {str(e)}")
                if attempt < 2:  # Si ce n'est pas la dernière tentative
                    print("Nouvelle tentative dans 3 secondes...")
                    time.sleep(3)
                else:
                    print("Abandon après 3 tentatives.")
                    break
        else:
            # Si la boucle for se termine sans break, c'est que toutes les tentatives ont échoué
            break
            
        # Si pas de données, sortir de la boucle while
        if data is None:
            break
    
    # Afficher les statistiques
    if nombre_organisations > 0:
        moyenne_revenus = total_revenus / nombre_organisations
        print(f"\nStatistiques:")
        print(f"Nombre d'organisations: {nombre_organisations}")
        print(f"Revenu total: ${total_revenus:,.2f}")
        print(f"Revenu moyen: ${moyenne_revenus:,.2f}")
    
    # Enregistrer les données
    if toutes_donnees:
        load(toutes_donnees, OUTPUT_FILE)
        print(f"\n{len(toutes_donnees)} organisations enregistrées au total.")
    else:
        print("Aucune donnée à enregistrer.")


# Point d'entrée du script
if __name__ == "__main__":
    main()