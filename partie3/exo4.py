from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Set
import json
import os
from datetime import datetime

# Modèles Pydantic
class PersonnageEvent(BaseModel):
    nom: str
    score: int

class SubscriptionRequest(BaseModel):
    type: str  # "console", "file", "webhook"
    active: bool
    destination: Optional[str] = None  # Chemin du fichier ou URL webhook

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Personnages avec Webhook et Notifications",
    description="Une API pour personnages fictifs avec système pub/sub",
    version="1.0.0"
)

# État des abonnements (en mémoire)
subscriptions = {
    "console": True,  # Console activée par défaut
    "file": True,     # Fichier activé par défaut
    "webhook": False  # Webhook désactivé par défaut
}

# Destination du fichier de notification
NOTIFICATION_FILE = "notifications.txt"

# Fonction pour enregistrer l'événement dans un fichier de log
def log_event(event: Dict[str, Any]):
    log_file = "webhook_log.json"
    
    # Ajouter un timestamp
    event_with_timestamp = event.copy()
    event_with_timestamp["timestamp"] = datetime.now().isoformat()
    
    # Lire les événements existants
    events = []
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    events = json.loads(content)
    except json.JSONDecodeError:
        print(f"Le fichier existe mais n'est pas un JSON valide. Création d'un nouveau fichier.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de log: {e}")
    
    # Ajouter le nouvel événement
    events.append(event_with_timestamp)
    
    # Écrire les événements mis à jour
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"Événement enregistré dans {log_file}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier de log: {e}")

# Fonction pour notifier les abonnés
# Version mise à jour de la fonction notify_subscribers
def notify_subscribers(event: Dict[str, Any]):
    # 1. Notification console
    if subscriptions["console"]:
        print(f"NOTIFICATION CONSOLE: Nouveau personnage ajouté - {event['nom']} (Niveau: {event['niveau']})")
    
    # 2. Notification fichier
    if subscriptions["file"]:
        try:
            with open(NOTIFICATION_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} - Nouveau personnage: {event['nom']} - Score: {event['score']} - Niveau: {event['niveau']}\n")
        except Exception as e:
            print(f"Erreur lors de l'écriture dans le fichier de notification: {e}")
    
    # 3. Appel à la route /notifier (nouvelle fonctionnalité)
    try:
        # Appel à la route locale /notifier
        import requests
        response = requests.get(
            f"http://localhost:8000/notifier?nom={event['nom']}&niveau={event['niveau']}",
            timeout=2  # Timeout de 2 secondes
        )
        if response.status_code == 200:
            badge_info = response.json()
            print(f"BADGE GÉNÉRÉ: {badge_info.get('display', 'Non disponible')}")
    except Exception as e:
        print(f"Erreur lors de l'appel à /notifier: {e}")
    
    # 4. Notification webhook (si configuré)
    if subscriptions["webhook"]:
        # Code pour le webhook...
        print("Notification webhook non configurée")

# Route webhook pour recevoir des événements de personnage
@app.post("/webhook/personnage", tags=["Webhooks"])
async def webhook_personnage(event: PersonnageEvent, background_tasks: BackgroundTasks):
    """
    Reçoit un événement webhook contenant des informations sur un personnage.
    Le score est utilisé pour déterminer le niveau du personnage.
    """
    print(f"Événement de personnage reçu: {event.dict()}")
    
    # Enrichissement : ajouter un niveau en fonction du score
    niveau = "débutant"
    if event.score >= 90:
        niveau = "légendaire"
    elif event.score >= 75:
        niveau = "expert"
    elif event.score >= 50:
        niveau = "intermédiaire"
    
    # Créer une réponse enrichie
    response = {
        "message": f"Événement reçu pour le personnage {event.nom}",
        "personnage": {
            "nom": event.nom,
            "score": event.score,
            "niveau": niveau
        }
    }
    
    # Enregistrer l'événement (publication)
    event_to_log = response["personnage"]
    background_tasks.add_task(log_event, event_to_log)
    
    # Notifier les abonnés (publication)
    background_tasks.add_task(notify_subscribers, event_to_log)
    
    return response

# Route pour s'abonner ou se désabonner aux notifications
@app.post("/subscribe", tags=["Notifications"])
async def subscribe(request: SubscriptionRequest):
    """
    Active ou désactive un type de notification.
    Types disponibles: console, file, webhook
    """
    if request.type not in subscriptions:
        raise HTTPException(status_code=400, detail=f"Type de notification invalide: {request.type}")
    
    subscriptions[request.type] = request.active
    
    return {
        "message": f"Notification {request.type} {'activée' if request.active else 'désactivée'}",
        "subscriptions": subscriptions
    }

# Route pour consulter l'état des abonnements
@app.get("/subscribe", tags=["Notifications"])
async def get_subscriptions():
    """
    Renvoie l'état actuel des abonnements aux notifications.
    """
    return {
        "subscriptions": subscriptions
    }

# Si ce fichier est exécuté directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


# Ajouter ce nouvel endpoint dans ton code existant
@app.get("/notifier", tags=["Notifications"])
async def notifier(nom: Optional[str] = None, niveau: Optional[str] = None):
    """
    Route qui affiche un badge ou une notification pour un personnage.
    Cette route peut être appelée par le système de notification.
    """
    if nom and niveau:
        # Formatage du badge en fonction du niveau
        badge = "🔶"  # Badge par défaut
        
        if niveau == "légendaire":
            badge = "⭐⭐⭐ LÉGENDAIRE ⭐⭐⭐"
        elif niveau == "expert":
            badge = "🥇 EXPERT 🥇"
        elif niveau == "intermédiaire":
            badge = "🔹 INTERMÉDIAIRE 🔹"
        elif niveau == "débutant":
            badge = "🔸 DÉBUTANT 🔸"
        
        return {
            "badge": badge,
            "message": f"Notification badge: {nom} a atteint le niveau {niveau}!",
            "display": f"{badge} {nom} {badge}"
        }
    else:
        return {
            "message": "Aucune notification à afficher. Utilisez ?nom=XXX&niveau=YYY pour tester."
        }