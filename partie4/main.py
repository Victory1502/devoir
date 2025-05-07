from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Set
import json
import os
from datetime import datetime

# Modèles Pydantic existants
class Personnage(BaseModel):
    id: int
    nom: str
    profession: str
    age: int
    pouvoir: str = None

class Score(BaseModel):
    name: str
    city: str
    state: Optional[str] = None
    avis: str
    score: int
    category: Optional[str] = None

# Nouveau modèle pour le traitement
class PersonnageTraitement(BaseModel):
    nom: str
    score: int
    score_double: Optional[int] = None

class PersonnageResponse(BaseModel):
    nom: str
    score: int
    score_double: Optional[int] = None
    niveau: str

# Modèle pour le webhook
class PersonnageEvent(BaseModel):
    nom: str
    score: int

class SubscriptionRequest(BaseModel):
    type: str  # "console", "file", "webhook"
    active: bool
    destination: Optional[str] = None

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Personnages",
    description="Une API pour personnages fictifs avec webhooks et traitement",
    version="1.0.0"
)

# État des abonnements (en mémoire)
subscriptions = {
    "console": True,  # Console activée par défaut
    "file": True,     # Fichier activé par défaut
    "webhook": False  # Webhook désactivé par défaut
}

# Configuration
TOKEN_VALIDE = "mon_super_token_secret"
NOTIFICATION_FILE = "notifications.txt"

# Middleware CORS si nécessaire
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fonction pour vérifier le token
async def verifier_token(token: Optional[str] = Header(None)):
    if token is None or token != TOKEN_VALIDE:
        raise HTTPException(
            status_code=401,
            detail="Token d'accès invalide ou manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# Fonction pour charger les personnages depuis le fichier JSON
def charger_personnages():
    try:
        if not os.path.exists("personnages.json"):
            return []
        
        with open("personnages.json", "r", encoding="utf-8") as f:
            return json.load(f)
        
    except Exception as e:
        print(f"Erreur lors du chargement des personnages: {e}")
        return []

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
def notify_subscribers(event: Dict[str, Any]):
    # 1. Notification console
    if subscriptions["console"]:
        print(f"NOTIFICATION CONSOLE: Nouveau personnage ajouté - {event['nom']} (Niveau: {event.get('niveau', 'N/A')})")
    
    # 2. Notification fichier
    if subscriptions["file"]:
        try:
            with open(NOTIFICATION_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} - Nouveau personnage: {event['nom']} - Score: {event.get('score', 'N/A')} - Niveau: {event.get('niveau', 'N/A')}\n")
        except Exception as e:
            print(f"Erreur lors de l'écriture dans le fichier de notification: {e}")
    
    # 3. Appel à la route /notifier
    try:
        # Appel à la route locale /notifier
        import requests
        response = requests.get(
            f"http://localhost:8000/notifier?nom={event['nom']}&niveau={event.get('niveau', 'débutant')}",
            timeout=2
        )
        if response.status_code == 200:
            badge_info = response.json()
            print(f"BADGE GÉNÉRÉ: {badge_info.get('display', 'Non disponible')}")
    except Exception as e:
        print(f"Erreur lors de l'appel à /notifier: {e}")
    
    # 4. Notification webhook
    if subscriptions["webhook"]:
        print("Notification webhook non configurée")

# Route pour l'endpoint GET /personnages
@app.get("/personnages", response_model=List[Personnage], tags=["Personnages"])
async def get_personnages(token: str = Depends(verifier_token)):
    """
    Récupère la liste complète des personnages fictifs.
    Nécessite un token d'authentification valide dans l'en-tête.
    """
    personnages = charger_personnages()
    if not personnages:
        raise HTTPException(status_code=404, detail="Aucun personnage trouvé")
    return personnages

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
    
    # Enregistrer l'événement et notifier les abonnés
    event_to_log = response["personnage"]
    background_tasks.add_task(log_event, event_to_log)
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

# Route pour générer un badge
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

# Nouvel endpoint pour le traitement des personnages
@app.post("/traitement", response_model=PersonnageResponse, tags=["Traitement"])
async def traiter_personnage(personnage: PersonnageTraitement):
    """
    Traite un personnage en calculant son niveau en fonction du score.
    
    Args:
        personnage: Données du personnage avec nom et score
        
    Returns:
        Personnage enrichi avec un niveau calculé
    """
    # Calcul du niveau en fonction du score
    niveau = "débutant"
    if personnage.score >= 90:
        niveau = "légendaire"
    elif personnage.score >= 75:
        niveau = "expert"
    elif personnage.score >= 50:
        niveau = "intermédiaire"
    
    # Créer la réponse enrichie
    response = {
        "nom": personnage.nom,
        "score": personnage.score,
        "niveau": niveau
    }
    
    # Inclure le score_double si présent
    if personnage.score_double is not None:
        response["score_double"] = personnage.score_double
    
    return response

# Page d'accueil
@app.get("/", tags=["Accueil"])
async def root():
    """
    Page d'accueil de l'API.
    """
    return {
        "message": "Bienvenue sur l'API de personnages et traitement!",
        "endpoints": {
            "personnages": "GET /personnages - Nécessite un token",
            "webhook": "POST /webhook/personnage - Pour recevoir des événements",
            "subscribe": "GET/POST /subscribe - Gérer les abonnements",
            "notifier": "GET /notifier - Générer un badge",
            "traitement": "POST /traitement - Traiter des personnages"
        }
    }

# Si on exécute ce fichier directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)