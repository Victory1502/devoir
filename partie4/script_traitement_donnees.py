import json
import requests
import time
import random
from typing import List, Dict, Any

# Configuration
API_ENDPOINT = "http://localhost:8000/traitement"
MAX_ITEMS = 15  # Nombre de personnages à générer
DELAY = 0.5  # Délai entre chaque requête (en secondes)
REQUEST_FILE = "personnages_requests.json"  # Fichier pour enregistrer les requêtes
RESPONSE_FILE = "personnages_responses.json"  # Fichier pour enregistrer les réponses

# Liste de noms de personnages de manga
PERSONNAGES_MANGA = [
    "Naruto Uzumaki", "Sasuke Uchiha", "Sakura Haruno", "Kakashi Hatake",
    "Monkey D. Luffy", "Roronoa Zoro", "Nami", "Sanji",
    "Ichigo Kurosaki", "Rukia Kuchiki", "Orihime Inoue", "Uryu Ishida",
    "Goku", "Vegeta", "Bulma", "Piccolo",
    "Edward Elric", "Alphonse Elric", "Roy Mustang", "Winry Rockbell",
    "Light Yagami", "L Lawliet", "Ryuk", "Misa Amane",
    "Eren Yeager", "Mikasa Ackerman", "Armin Arlert", "Levi Ackerman",
    "Spike Spiegel", "Faye Valentine", "Jet Black", "Edward Wong",
    "Gon Freecss", "Killua Zoldyck", "Kurapika", "Leorio Paradinight",
    "Ash Ketchum", "Misty", "Brock", "Pikachu",
    "Saitama", "Genos", "Tatsumaki", "King",
    "Izuku Midoriya", "Katsuki Bakugo", "Ochaco Uraraka", "All Might",
    "Senku Ishigami", "Taiju Oki", "Yuzuriha Ogawa", "Chrome",
    "Tanjiro Kamado", "Nezuko Kamado", "Zenitsu Agatsuma", "Inosuke Hashibira",
    "Yuji Itadori", "Megumi Fushiguro", "Nobara Kugisaki", "Satoru Gojo"
]

def generer_personnages(nombre: int) -> List[Dict[str, Any]]:
    """
    Génère une liste de personnages manga avec des scores aléatoires.
    
    Args:
        nombre: Nombre de personnages à générer
        
    Returns:
        Liste de dictionnaires contenant nom et score
    """
    print(f"Génération de {nombre} personnages manga...")
    
    # Mélanger la liste pour obtenir des personnages aléatoires
    personnages_disponibles = PERSONNAGES_MANGA.copy()
    random.shuffle(personnages_disponibles)
    
    # Limiter au nombre demandé
    if nombre > len(personnages_disponibles):
        nombre = len(personnages_disponibles)
        print(f"Limité à {nombre} personnages disponibles.")
    
    # Générer les personnages avec scores
    personnages = []
    for i in range(nombre):
        nom = personnages_disponibles[i]
        
        # Générer un score entre 1 et 100
        score = random.randint(1, 100)
        
        # Ajouter le personnage à la liste
        personnage = {
            "nom": nom,
            "score": score,
            "score_double": score * 2
        }
        
        personnages.append(personnage)
    
    print(f"{len(personnages)} personnages générés.")
    return personnages

def sauvegarder_fichier(donnees: List[Dict[str, Any]], fichier: str) -> None:
    """
    Sauvegarde des données dans un fichier JSON.
    
    Args:
        donnees: Données à sauvegarder
        fichier: Nom du fichier
    """
    try:
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=2, ensure_ascii=False)
        print(f"Données sauvegardées dans {fichier}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde dans {fichier}: {e}")

def envoyer_donnees(donnees: List[Dict[str, Any]], endpoint: str) -> List[Dict[str, Any]]:
    """
    Envoie les données à l'API et récupère les réponses.
    
    Args:
        donnees: Liste des données à envoyer
        endpoint: URL de l'endpoint API
        
    Returns:
        Liste des réponses de l'API
    """
    print(f"Envoi de {len(donnees)} personnages à l'API...")
    reponses = []
    
    # Enregistrer les requêtes avant de les envoyer
    sauvegarder_fichier(donnees, REQUEST_FILE)
    print(f"Les personnages à envoyer ont été enregistrés dans {REQUEST_FILE}")
    
    for i, item in enumerate(donnees, 1):
        try:
            print(f"[{i}/{len(donnees)}] Envoi de {item['nom']}...")
            
            # Envoyer la requête POST
            response = requests.post(
                endpoint,
                json=item,
                headers={"Content-Type": "application/json"}
            )
            
            # Vérifier le statut de la réponse
            if response.status_code == 200:
                reponse = response.json()
                reponses.append(reponse)
                print(f"  ✅ Réponse reçue: {reponse['nom']} - Niveau: {reponse['niveau']}")
            else:
                print(f"  ❌ Erreur {response.status_code}: {response.text}")
            
            # Pause pour éviter de surcharger l'API
            time.sleep(DELAY)
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'envoi: {str(e)}")
            time.sleep(DELAY)
    
    # Enregistrer les réponses
    if reponses:
        sauvegarder_fichier(reponses, RESPONSE_FILE)
        print(f"Les réponses reçues ont été enregistrées dans {RESPONSE_FILE}")
    
    return reponses

def afficher_resume(reponses: List[Dict[str, Any]]) -> None:
    """
    Affiche un résumé des réponses reçues.
    
    Args:
        reponses: Liste des réponses à résumer
    """
    print("\n=== RÉSUMÉ DES RÉSULTATS ===")
    print(f"Nombre total de personnages traités: {len(reponses)}")
    
    # Compter les personnages par niveau
    niveaux = {}
    for reponse in reponses:
        niveau = reponse.get("niveau", "inconnu")
        niveaux[niveau] = niveaux.get(niveau, 0) + 1
    
    # Afficher les statistiques par niveau
    print("\nRépartition par niveau:")
    for niveau, compte in sorted(niveaux.items(), key=lambda x: x[1], reverse=True):
        print(f"  {niveau}: {compte} personnage(s) ({compte / len(reponses) * 100:.1f}%)")
    
    # Afficher quelques exemples par niveau
    print("\nExemples par niveau:")
    niveaux_exemples = {}
    
    # Regrouper les personnages par niveau
    for reponse in reponses:
        niveau = reponse.get("niveau", "inconnu")
        if niveau not in niveaux_exemples:
            niveaux_exemples[niveau] = []
        niveaux_exemples[niveau].append(reponse)
    
    # Afficher des exemples pour chaque niveau
    for niveau, exemples in niveaux_exemples.items():
        print(f"\n  Niveau {niveau}:")
        for i, exemple in enumerate(exemples[:3], 1):
            print(f"    - {exemple['nom']} (Score: {exemple['score']})")
        if len(exemples) > 3:
            print(f"    ... et {len(exemples) - 3} autres")

def main():
    # Étape 1: Générer des personnages
    personnages = generer_personnages(MAX_ITEMS)
    if not personnages:
        print("Aucun personnage généré. Fin du programme.")
        return
    
    # Étape 2: Envoyer les personnages à l'API
    reponses = envoyer_donnees(personnages, API_ENDPOINT)
    
    # Étape 3: Afficher un résumé des résultats
    if reponses:
        afficher_resume(reponses)
    else:
        print("Aucune réponse reçue de l'API.")

if __name__ == "__main__":
    main()