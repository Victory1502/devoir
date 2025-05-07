from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os

# Modèles Pydantic
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

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Personnages et Scores",
    description="Une API pour personnages fictifs et scores d'organisations",
    version="1.0.0"
)

# Configuration CORS
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

# Token de sécurité valide
TOKEN_VALIDE = "mon_super_token_secret"

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

# Fonction pour charger les scores depuis le fichier JSON
def charger_scores():
    try:
        if not os.path.exists("scores.json"):
            return []
        
        with open("scores.json", "r", encoding="utf-8") as f:
            return json.load(f)
        
    except Exception as e:
        print(f"Erreur lors du chargement des scores: {e}")
        return []

# Fonction pour sauvegarder les scores
def sauvegarder_scores(scores):
    try:
        with open("scores.json", "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des scores: {e}")
        return False

# Endpoint GET pour récupérer tous les personnages
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

# Endpoint GET pour récupérer tous les scores
@app.get("/scores", response_model=List[Score], tags=["Scores"])
async def get_scores(token: str = Depends(verifier_token)):
    """
    Récupère la liste complète des scores.
    Nécessite un token d'authentification valide dans l'en-tête.
    """
    scores = charger_scores()
    if not scores:
        return []
    return scores

# Endpoint POST pour ajouter un score
@app.post("/scores", response_model=Dict[str, Any], tags=["Scores"])
async def add_score(score: Score, token: str = Depends(verifier_token)):
    """
    Ajoute un nouveau score.
    Nécessite un token d'authentification valide dans l'en-tête.
    """
    # Charger les scores existants
    scores = charger_scores()
    
    # Vérifier si un score avec le même nom et la même ville existe déjà
    for existing_score in scores:
        if existing_score.get("name") == score.name and existing_score.get("city") == score.city:
            return {"status": "already_exists", "message": "Un score existe déjà pour cette organisation"}
    
    # Ajouter le nouveau score
    scores.append(score.dict())
    
    # Sauvegarder les scores
    if sauvegarder_scores(scores):
        return {"status": "success", "message": "Score ajouté avec succès"}
    else:
        raise HTTPException(status_code=500, detail="Erreur lors de la sauvegarde du score")

# Page d'accueil
@app.get("/", tags=["Accueil"])
async def root():
    """
    Page d'accueil de l'API.
    """
    return {
        "message": "Bienvenue sur l'API! Accédez à /docs pour la documentation.",
        "endpoints": {
            "personnages": "GET /personnages - Nécessite un token",
            "scores": "GET /scores - Nécessite un token",
            "add_score": "POST /scores - Nécessite un token"
        }
    }

# Si on exécute ce fichier directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)