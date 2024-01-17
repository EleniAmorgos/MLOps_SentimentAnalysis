from fastapi import FastAPI, HTTPException,status,Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from typing import Optional, List
import asyncio
import csv
import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from time import time

import jwt

from datetime import datetime, timedelta


from src.data.web_scrapping import WebScrapping_RatedComments
from src.features.build_features import Process_Comments

api = FastAPI(
    title="API Sentiment analysis",
    description="API permettant l'analyse de sentiments depuis un texte",
    version="1.0.1",
    openapi_tags=[
        {'name': 'home', 'description': 'Fonctions de base'},
        {'name': 'security', 'description': 'Fonctions réservées à la sécurisation de l API'},
        {'name': 'sentiment_analysis', 'description': 'Fonctions d analyse des sentiments'},
        {'name': 'scrapping', 'description': 'Fonctions réservées à la génération de nouvelles données'},
        {'name': 'data management', 'description': 'Fonctions réservées à la génération de nouvelles données'},
        {'name': 'training', 'description': 'Fonctions réservées l entrainement de modèles'}
]
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration pour le JWT
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Scrapping_Request(BaseModel):
    """ Représente une requête de scrapping.

    Attributes:
        • liste_sites : liste d'enseignes pour lesquelles on va scrapper les pages Trustpilor
        • nbr_pages: nbr de pages
    """
    liste_sites : List
    nbr_pages: Optional[int] = 1

users_db = {

    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash('wonderland'),
        "role" : ["user"],
    },
    "bob": {
        "username": "bob",
        "hashed_password": pwd_context.hash('builder'),
        "role" : ["user"],
    },
    "clementine": {
        "username": "clementine",
        "hashed_password": pwd_context.hash('mandarine'),
        "role" : ["user"],
    },
    "admin" : {
        "username" :  "admin",
        "hashed_password" : pwd_context.hash('TFH_dstMLOPS23'),
        "role" : ["user", "admin"],
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    token_data = TokenData(username=username)
    user = users_db.get(username, None)
    if user is None:
        raise credentials_exception
    return user

@api.post("/token", response_model=Token, tags=['security'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Description:
    Cette route permet à un utilisateur de s'authentifier en fournissant un nom d'utilisateur et un mot de passe. Si l'authentification est réussie, elle renvoie un jeton d'accès JWT.

    Args:
    - form_data (OAuth2PasswordRequestForm, dépendance): Les données de formulaire contenant le nom d'utilisateur et le mot de passe.

    Returns:
    - Token: Un modèle de jeton d'accès JWT.

    Raises:
    - HTTPException(400, detail="Incorrect username or password"): Si l'authentification échoue en raison d'un nom d'utilisateur ou d'un mot de passe incorrect, une exception HTTP 400 Bad Request est levée.
    """
    try:
        user = users_db.get(form_data.username)
        if user:
            hashed_password = user.get("hashed_password")
            if not user or not verify_password(form_data.password, hashed_password):
                raise HTTPException(status_code=400, detail="Username ou password incorrect")

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
            access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)

            return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        # Log the exception or print the details for debugging
        print(f"Exception during authentication: {e}")
    # If any exception occurs or authentication fails, raise HTTPException
    raise HTTPException(status_code=400, detail="Username ou password incorrect")

@api.get('/', tags=['home'])
async def get_item():
    """Point de terminaison pour vérifier que l'API est bien fonctionnelle 

    Returns :
        dict : message iniquant que l'API fonctionne correctement
    """
    return {'message' : 'API fonctionnelle'}

@api.get("/secured", tags=['home'])
def read_private_data(current_user: str = Depends(get_current_user)):
    """
    Description:
    Cette route renvoie un message "Hello World, but secured!" uniquement si l'utilisateur est authentifié.

    Args:
    - current_user (str, dépendance): Le nom d'utilisateur de l'utilisateur actuellement authentifié.

    Returns:
    - JSON: Renvoie un JSON contenant un message de salutation sécurisé si l'utilisateur est authentifié, sinon une réponse non autorisée.

    Raises:
    - HTTPException(401, detail="Unauthorized"): Si l'utilisateur n'est pas authentifié, une exception HTTP 401 Unauthorized est levée.
    """

    return {"message": "Accès au endpoint securisé avec succès !"}






@api.post('/scrap_last30days', tags=['scrapping'])
async def scrap_last30days(scrap_request: Scrapping_Request, current_user: str = Depends(get_current_user)):
    """
    Endpoint pour scrapper. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        scrap_request (Scrapping_Request): Les données de la requete.
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si la création a réussi.
    """
    if "admin" not in current_user["role"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission refusée. Seul un administrateur peut scrapper des données",
        )

    scrap_request_dict = {
        'liste_sites': scrap_request.liste_sites ,
        'nbr_pages': scrap_request.nbr_pages
    }
    
    # Nom du CSV où les données seront écrites
    csv_filename = 'scrapped_comments.csv'
    # Répertoire de données depuis le répertoire src
    external_data_path = os.path.join( '..', 'data', 'external')
    # print(external_data_path)
    # Si le répertoire n'existe pas, on le crée
    os.makedirs(external_data_path, exist_ok=True)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath = os.path.join(external_data_path, csv_filename)
    print(csv_filepath)

    df = WebScrapping_RatedComments.WebScrapping_Comments(liste_sites=scrap_request_dict['liste_sites'], nbr_pages = scrap_request_dict['nbr_pages'])

    print("Longueur du df : ", len(df))
    print(df.head(10))
    print(df.tail(10))

    # Save the DataFrame to CSV
    df.to_csv(csv_filepath, sep=';', quotechar='"', index=False)

    return {'message': f"Data written to: {csv_filepath} {str(len(df))} rows" }



@api.post('/process_comments', tags=['data management'])
async def process_comments(current_user: str = Depends(get_current_user)):
    """
    Endpoint pour processer les commentaires scrappés. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si le data processing a réussi.
    """
    if "admin" not in current_user["role"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission refusée. Seul un administrateur peut processer des données",
        )

    # Nom du CSV où les données sont lues
    csv_filename_input = 'scrapped_comments.csv'
    # Répertoire de données depuis le répertoire src
    external_data_path = os.path.join( '..', 'data', 'external')
    print("external_data_path : ",external_data_path)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath_input = os.path.join(external_data_path, csv_filename_input)
    print("csv_filepath_input : ", csv_filepath_input)
    # Vérifier l'existence du répertoire
    if not os.path.exists(external_data_path) or not os.path.isdir(external_data_path):
        print(f"Le répertoire {external_data_path} n'existe pas.")
        exit()
    # Vérifier l'existence du fichier
    if not os.path.exists(csv_filepath_input) or not os.path.isfile(csv_filepath_input):
        print(f"Le fichier {csv_filepath_input} n'existe pas.")
        exit()

    # Le répertoire et le fichier existent, poursuivre avec le reste du code
    print(f"Le répertoire {external_data_path} et le fichier {csv_filepath_input} existent.")


    # Nom du CSV où les données seront écrites
    csv_filename_output = 'scrapped_comments_processed.csv'
    print("csv_filename_output : ", csv_filename_output)
    # Répertoire de données depuis le répertoire src
    interim_data_path = os.path.join( '..', 'data', 'interim')
    print("interim_data_path :" , interim_data_path)
    # Si le répertoire n'existe pas, on le crée
    os.makedirs(interim_data_path, exist_ok=True)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath_output = os.path.join(interim_data_path, csv_filename_output)
    print("csv_filepath_output : ", csv_filepath_output)


    df = Process_Comments.Process_Comments_Notes(csv_filepath_input)

    df.to_csv(csv_filepath_output, sep=';', quotechar='"', index=False)

    return {'message': f"Data written to: {csv_filepath_output} {str(len(df))} rows" }




@api.post('/histo_process_comments', tags=['data management'])
async def histo_process_comments(current_user: str = Depends(get_current_user)):
    """
    Endpoint pour historiser les commentaires scrappés. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si le data processing a réussi.
    """
    if "admin" not in current_user["role"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission refusée. Seul un administrateur peut historiser des données",
        )

    # Nom du CSV où les données à historiser sont lues
    csv_filename_input = 'scrapped_comments_processed.csv'
    # Répertoire de données depuis le répertoire src
    interim_data_path = os.path.join( '..', 'data', 'interim')
    print("interim_data_path : ",interim_data_path)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath_input = os.path.join(interim_data_path, csv_filename_input)
    print("csv_filepath_input : ", csv_filepath_input)
    # Vérifier l'existence du répertoire
    if not os.path.exists(interim_data_path) or not os.path.isdir(interim_data_path):
        print(f"Le répertoire {interim_data_path} n'existe pas.")
        exit()
    # Vérifier l'existence du fichier
    if not os.path.exists(csv_filepath_input) or not os.path.isfile(csv_filepath_input):
        print(f"Le fichier {csv_filepath_input} n'existe pas.")
        exit()
    # Le répertoire et le fichier existent, poursuivre avec le reste du code
    print(f"Le répertoire {interim_data_path} et le fichier {csv_filepath_input} existent.")

    # Nom du CSV où les données déjà historisées sont lues puis réécrites après ajout des nouvelles données
    csv_filename_histo = 'processed_comments_histo.csv'
    # Répertoire de données depuis le répertoire src
    processed_data_path = os.path.join( '..', 'data', 'processed')
    print("processed_data_path : ",processed_data_path)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath_histo = os.path.join(processed_data_path, csv_filename_histo)
    print("csv_filepath_histo : ", csv_filepath_histo)
    # Vérifier l'existence du répertoire
    if not os.path.exists(processed_data_path) or not os.path.isdir(processed_data_path):
        print(f"Le répertoire {processed_data_path} n'existe pas.")
        exit()
    # Vérifier l'existence du fichier
    if not os.path.exists(csv_filepath_histo) or not os.path.isfile(csv_filepath_histo):
        print(f"Le fichier {csv_filepath_histo} n'existe pas.")
        exit()

    # Le répertoire et le fichier existent, poursuivre avec le reste du code
    print(f"Le répertoire {processed_data_path} et le fichier {csv_filepath_histo} existent.")

    result_dico = Process_Comments.Histo_New_Comments(csv_filepath_input,csv_filepath_histo)
    df_result = result_dico['df_result']
    df_result.to_csv(csv_filepath_histo, sep=';', quotechar='"', index=False)
    print (result_dico['nb_rows_input'], result_dico['nb_rows_histo'], result_dico['nb_rows_added_to_histo'], len(df_result))

    return {'message': f"Data written to: {csv_filepath_histo} : {str(result_dico['nb_rows_added_to_histo'])} rows added to {str(result_dico['nb_rows_histo'])} in histo : {str(len(df_result))} in total"}
