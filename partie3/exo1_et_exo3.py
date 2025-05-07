from fastapi import FastAPI, HTTPException, Header, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime

# Modèles Pydantic existants (garde tes modèles actuels)
class Personnage(BaseModel):
    id: int
    nom: str
    profession: str
    age: int
    pouvoir: str = None

# Nouveau modèle pour le webhook
class PersonnageEvent(BaseModel):
    nom: str
    score: int

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Personnages avec Webhook",
    description="Une API pour personnages fictifs avec support d'événements webhook",
    version="1.0.0"
)

# Fonction pour enregistrer l'événement dans un fichier de log
# def log_event(event: Dict[str, Any]):
#     log_dir = "logs"
#     os.makedirs(log_dir, exist_ok=True)
    
#     log_file = os.path.join(log_dir, "webhook_events.json")
    
#     # Ajouter un timestamp
#     event_with_timestamp = event.copy()
#     event_with_timestamp["timestamp"] = datetime.now().isoformat()
    
#     # Lire les événements existants
#     events = []
#     try:
#         if os.path.exists(log_file):
#             with open(log_file, "r", encoding="utf-8") as f:
#                 events = json.load(f)
#     except Exception as e:
#         print(f"Erreur lors de la lecture du fichier de log: {e}")
    
#     # Ajouter le nouvel événement
#     events.append(event_with_timestamp)
    
#     # Écrire les événements mis à jour
#     try:
#         with open(log_file, "w", encoding="utf-8") as f:
#             json.dump(events, f, indent=2, ensure_ascii=False)
#     except Exception as e:
#         print(f"Erreur lors de l'écriture du fichier de log: {e}")



# Fonction pour enregistrer l'événement dans un fichier de log
def log_event(event: Dict[str, Any]):
    log_file = "webhook_log.json"
    
    # Ajouter un timestamp
    event_with_timestamp = event.copy()
    event_with_timestamp["timestamp"] = datetime.now().isoformat()
    
    # Lire les événements existants (si le fichier existe)
    events = []
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # Vérifier que le fichier n'est pas vide
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
    
    # Enregistrer l'événement de manière asynchrone (pour ne pas bloquer la réponse)
    event_to_log = {
        "type": "personnage_event",
        "data": {
            "nom": event.nom,
            "score": event.score,
            "niveau": niveau
        }
    }
    background_tasks.add_task(log_event, event_to_log)
    
    return response

# Garde tes autres routes existantes...

# Si ce fichier est exécuté directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)