# exos 1 

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List
# import json
# import os


# class Personnage(BaseModel):  # Correction: BasModel -> BaseModel
#     id: int
#     nom: str
#     profession: str
#     age: int
#     pouvoir: str = None


# app = FastAPI(
#     title="API de Personnages Fictifs",
#     description="Une API simple pour afficher des personnages fictifs",
#     version="1.0.0"
# )

# def charger_personnages():  # Correction: chargher_personnage -> charger_personnages
#     try:
#         if not os.path.exists("personnages.json"):
#             return []
        
#         with open("personnages.json", "r", encoding="utf-8") as f:
#             return json.load(f)
        
#     except Exception as e:
#         print(f"Erreur lors du chargement des personnages: {e}")
#         return []
    
# @app.get("/personnages", response_model=List[Personnage], tags=["Personnages"])
# async def get_personnages():
#     """
#     Récupère la liste complète des personnages fictifs.
#     """
#     personnages = charger_personnages()  # Correction: appeler la fonction au lieu d'utiliser personnages_db
#     if not personnages:
#         raise HTTPException(status_code=404, detail="Aucun personnage trouvé")
#     return personnages

# # Page d'accueil
# @app.get("/", tags=["Accueil"])
# async def root():
#     """
#     Page d'accueil de l'API.
#     """
#     return {"message": "Bienvenue sur l'API de personnages fictifs! Accédez à /docs pour la documentation."}

# # Si on exécute ce fichier directement
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


# exos 2


# from fastapi import FastAPI, HTTPException, Header, Depends
# from pydantic import BaseModel
# from typing import List, Optional
# import json
# import os


# class Personnage(BaseModel):
#     id: int
#     nom: str
#     profession: str
#     age: int
#     pouvoir: str = None


# app = FastAPI(
#     title="API de Personnages Fictifs",
#     description="Une API simple pour afficher des personnages fictifs",
#     version="1.0.0"
# )

# # Token de sécurité valide (idéalement, cela devrait être stocké de manière plus sécurisée)
# TOKEN_VALIDE = "mon_super_token_secret"

# def charger_personnages():
#     try:
#         if not os.path.exists("personnages.json"):
#             return []
        
#         with open("personnages.json", "r", encoding="utf-8") as f:
#             return json.load(f)
        
#     except Exception as e:
#         print(f"Erreur lors du chargement des personnages: {e}")
#         return []

# # Fonction pour vérifier le token
# async def verifier_token(token: Optional[str] = Header(None)):
#     if token is None or token != TOKEN_VALIDE:
#         raise HTTPException(
#             status_code=401,
#             detail="Token d'accès invalide ou manquant",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return token
    
# @app.get("/personnages", response_model=List[Personnage], tags=["Personnages"])
# async def get_personnages(token: str = Depends(verifier_token)):
#     """
#     Récupère la liste complète des personnages fictifs.
#     Nécessite un token d'authentification valide dans l'en-tête.
#     """
#     personnages = charger_personnages()
#     if not personnages:
#         raise HTTPException(status_code=404, detail="Aucun personnage trouvé")
#     return personnages

# # Page d'accueil
# @app.get("/", tags=["Accueil"])
# async def root():
#     """
#     Page d'accueil de l'API.
#     """
#     return {"message": "Bienvenue sur l'API de personnages fictifs! Accédez à /docs pour la documentation. L'endpoint /personnages nécessite un token."}

# # Si on exécute ce fichier directement
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


# exos 3


from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os


class Personnage(BaseModel):
    id: int
    nom: str
    profession: str
    age: int
    pouvoir: str = None


app = FastAPI(
    title="API de Personnages Fictifs",
    description="Une API simple pour afficher des personnages fictifs",
    version="1.0.0"
)

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:8080",  # Pour Vue
   
]

# Ajout du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Liste des origines autorisées
    allow_credentials=True,     # Permet l'envoi de cookies
    allow_methods=["*"],        # Autorise toutes les méthodes HTTP
    allow_headers=["*"],        # Autorise tous les en-têtes HTTP
)

# Token de sécurité valide
TOKEN_VALIDE = "mon_super_token_secret"

def charger_personnages():
    try:
        if not os.path.exists("personnages.json"):
            return []
        
        with open("personnages.json", "r", encoding="utf-8") as f:
            return json.load(f)
        
    except Exception as e:
        print(f"Erreur lors du chargement des personnages: {e}")
        return []

# Fonction pour vérifier le token
async def verifier_token(token: Optional[str] = Header(None)):
    if token is None or token != TOKEN_VALIDE:
        raise HTTPException(
            status_code=401,
            detail="Token d'accès invalide ou manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
    
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

# Page d'accueil
@app.get("/", tags=["Accueil"])
async def root():
    """
    Page d'accueil de l'API.
    """
    return {"message": "Bienvenue sur l'API de personnages fictifs! Accédez à /docs pour la documentation. L'endpoint /personnages nécessite un token."}

# Si on exécute ce fichier directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)