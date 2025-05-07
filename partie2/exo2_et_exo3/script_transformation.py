import json
import requests
import time
import os
from typing import List, Dict, Any
import random
from tqdm import tqdm  # Pour la barre de progression (bonus)

# Configuration
API_URL = "http://localhost:8000/scores"
TOKEN = "mon_super_token_secret"
INPUT_FILE = "c:/Users/dimbo/Documents/Master 1 data ingenieur/Solution d'échange inter-applicatif/exos2/exo2/associations_chat.json"
LOG_FILE = "c:/Users/dimbo/Documents/Master 1 data ingenieur/Solution d'échange inter-applicatif/exos2/exo2/api_post_log.txt"
DELAY = 0.5  # Délai entre chaque requête (en secondes)
MAX_ITEMS = 50  # Limiter le nombre d'items pour ce test

# Fonction pour lire les données du fichier JSON
def read_data(filename: str) -> List[Dict[str, Any]]:
    """
    Lit les données à partir du fichier JSON spécifié.
    
    Args:
        filename: Chemin vers le fichier JSON
        
    Returns:
        Liste des données lues depuis le fichier
    """
    try:
        print(f"Lecture des données depuis {filename}...")
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"{len(data)} éléments trouvés dans le fichier.")
        return data
    
    except FileNotFoundError:
        print(f"Erreur: Le fichier {filename} n'existe pas.")
        return []
    
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier {filename} n'est pas un JSON valide.")
        return []
    
    except Exception as e:
        print(f"Erreur lors de la lecture des données: {str(e)}")
        return []

# Fonction pour transformer les données
def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme les données en ajoutant un champ avis et en renommant certains champs.
    
    Args:
        data: Liste des données à transformer
        
    Returns:
        Liste des données transformées
    """
    transformed_data = []
    
    print("Transformation des données...")
    
    for item in data:
        # Ne conserver que les éléments qui ont au moins un nom et une ville
        if item.get("name") and item.get("city"):
            # Calculer un score aléatoire entre 1 et 100
            score = random.randint(1, 100)
            
            # Déterminer l'avis basé sur le score
            if score >= 75:
                avis = "excellent"
            elif score >= 50:
                avis = "bon"
            elif score >= 25:
                avis = "moyen"
            else:
                avis = "faible"
            
            # Créer un nouvel objet avec uniquement les champs nécessaires
            transformed_item = {
                "name": item.get("name"),
                "city": item.get("city"),
                "state": item.get("state"),
                "score": score,
                "avis": avis,
                "category": item.get("ntee_code")
            }
            
            transformed_data.append(transformed_item)
    
    print(f"{len(transformed_data)} éléments après transformation.")
    return transformed_data

# Fonction pour envoyer les données à l'API
def send_data(data: List[Dict[str, Any]], api_url: str, token: str, max_items: int = None) -> Dict[str, int]:
    """
    Envoie les données transformées à l'API.
    
    Args:
        data: Liste des données à envoyer
        api_url: URL de l'API
        token: Token d'authentification
        max_items: Nombre maximum d'éléments à envoyer (facultatif)
        
    Returns:
        Dictionnaire avec les statistiques de succès/échec
    """
    # Configuration des en-têtes HTTP
    headers = {
        "token": token,
        "Content-Type": "application/json"
    }
    
    # Statistiques
    stats = {
        "success": 0,
        "already_exists": 0,
        "error": 0
    }
    
    # Initialiser le fichier de log
    with open(LOG_FILE, "w", encoding="utf-8") as log_file:
        log_file.write("=== Log d'envoi des données à l'API ===\n\n")
    
    # Limiter le nombre d'éléments si nécessaire
    if max_items and max_items < len(data):
        data = data[:max_items]
    
    print(f"Envoi de {len(data)} éléments à l'API...")
    
    # Utiliser tqdm pour afficher une barre de progression
    for item in tqdm(data, desc="Envoi des données", unit="item"):
        try:
            # Envoyer la requête POST
            response = requests.post(api_url, json=item, headers=headers)
            
            # Analyser la réponse
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get("status") == "success":
                    stats["success"] += 1
                    log_status = "SUCCÈS"
                elif response_data.get("status") == "already_exists":
                    stats["already_exists"] += 1
                    log_status = "DÉJÀ EXISTANT"
                else:
                    stats["error"] += 1
                    log_status = "ERREUR"
                
                # Écrire dans le fichier de log
                with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{log_status} - {item['name']} ({item['city']}) - {response_data.get('message')}\n")
            
            else:
                stats["error"] += 1
                
                # Écrire dans le fichier de log
                with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                    log_file.write(f"ERREUR - {item['name']} ({item['city']}) - Code: {response.status_code}\n")
                    
                    # Essayer d'afficher plus de détails sur l'erreur
                    try:
                        error_detail = response.json().get("detail", "Aucun détail")
                        log_file.write(f"  Détail: {error_detail}\n")
                    except:
                        log_file.write("  Pas de détails disponibles\n")
            
            # Pause pour éviter de surcharger l'API
            time.sleep(DELAY)
            
        except requests.RequestException as e:
            stats["error"] += 1
            
            # Écrire dans le fichier de log
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"ERREUR DE CONNEXION - {item['name']} ({item['city']}) - {str(e)}\n")
            
            print(f"Erreur de connexion: {str(e)}")
            time.sleep(DELAY)
    
    return stats

# Fonction de test unitaire pour vérifier l'ajout du champ "avis"
def test_avis_field(data: List[Dict[str, Any]], transformed_data: List[Dict[str, Any]]) -> bool:
    """
    Vérifie que le champ "avis" a bien été ajouté à toutes les données transformées.
    
    Args:
        data: Données originales
        transformed_data: Données transformées
        
    Returns:
        True si tous les éléments transformés ont un champ "avis", False sinon
    """
    if not transformed_data:
        return False
    
    for item in transformed_data:
        if "avis" not in item:
            return False
    
    return True

# Fonction principale
def main():
    # Lire les données
    data = read_data(INPUT_FILE)
    
    if not data:
        print("Aucune donnée à traiter. Arrêt du programme.")
        return
    
    # Transformer les données
    transformed_data = transform_data(data)
    
    if not transformed_data:
        print("Aucune donnée après transformation. Arrêt du programme.")
        return
    
    # Exécuter le test unitaire
    test_result = test_avis_field(data, transformed_data)
    print(f"Test unitaire - Vérification du champ 'avis': {'SUCCÈS' if test_result else 'ÉCHEC'}")
    
    if not test_result:
        print("Le test unitaire a échoué. Vérifiez votre fonction de transformation.")
        return
    
    # Envoyer les données à l'API
    stats = send_data(transformed_data, API_URL, TOKEN, MAX_ITEMS)
    
    # Afficher les statistiques
    print("\nRésultats de l'envoi des données:")
    print(f"  - Succès: {stats['success']}")
    print(f"  - Déjà existants: {stats['already_exists']}")
    print(f"  - Erreurs: {stats['error']}")
    print(f"Log détaillé disponible dans: {os.path.abspath(LOG_FILE)}")

# Point d'entrée du script
if __name__ == "__main__":
    main()