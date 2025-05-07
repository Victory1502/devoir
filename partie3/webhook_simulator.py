import requests
import json
import time
import random
from pprint import pprint

# Configuration
WEBHOOK_URL = "http://localhost:8000/webhook/personnage"
PERSONNAGES = [
    {"nom": "Naruto", "score": 85},
    {"nom": "Sasuke", "score": 87},
    {"nom": "Sakura", "score": 78},
    {"nom": "Kakashi", "score": 95},
    {"nom": "Hinata", "score": 72},
    {"nom": "Gaara", "score": 89},
    {"nom": "Rock Lee", "score": 68},
    {"nom": "Itachi", "score": 98},
    {"nom": "Jiraiya", "score": 91},
    {"nom": "Tsunade", "score": 93}
]

def envoyer_evenement(personnage):
    """
    Envoie un événement webhook pour un personnage donné.
    
    Args:
        personnage: Dictionnaire contenant les informations du personnage
    
    Returns:
        La réponse de l'API
    """
    try:
        print(f"Envoi d'un événement pour {personnage['nom']} (score: {personnage['score']})...")
        
        # Envoyer la requête POST
        response = requests.post(
            WEBHOOK_URL,
            json=personnage,
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier le code de statut
        if response.status_code == 200:
            print(f"Événement envoyé avec succès !")
            return response.json()
        else:
            print(f"Erreur lors de l'envoi de l'événement: Status code {response.status_code}")
            print(f"Réponse: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Erreur de connexion: {str(e)}")
        return None

def main():
    """
    Fonction principale qui simule l'envoi de plusieurs événements webhook.
    """
    print("=== Simulateur d'événements webhook pour personnages ===")
    print(f"URL cible: {WEBHOOK_URL}\n")
    
    # Option 1: Envoyer tous les personnages
    for personnage in PERSONNAGES:
        reponse = envoyer_evenement(personnage)
        if reponse:
            print("Réponse reçue:")
            pprint(reponse)
            print("=" * 40)
        
        # Pause pour éviter de surcharger l'API
        time.sleep(1)
    
    # Option 2: Envoyer un personnage aléatoire
    #personnage = random.choice(PERSONNAGES)
    #reponse = envoyer_evenement(personnage)
    #if reponse:
    #    print("Réponse reçue:")
    #    pprint(reponse)
    
    print("\nSimulation terminée.")

if __name__ == "__main__":
    main()