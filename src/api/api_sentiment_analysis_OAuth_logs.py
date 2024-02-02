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
import json
import jwt
import pickle
import numpy as np
import sklearn
import logging

from jwt.exceptions import ExpiredSignatureError, DecodeError

from datetime import datetime, timedelta

from data.web_scrapping import WebScrapping_RatedComments
from features.build_features import Process_Comments
from predictions.prediction_class import Predict_Sentiments

api = FastAPI(
    title="API Sentiment analysis",
    description="API permettant l'analyse de sentiments depuis un texte",
    version="1.0.1",
    openapi_tags=[
        {'name': 'home', 'description': 'Fonctions de base'},
        {'name': 'security', 'description': 'Fonctions réservées à la sécurisation de l API'},
        {'name': 'scrapping', 'description': 'Fonctions réservées à la génération de nouvelles données'},
        {'name': 'data management', 'description': 'Fonctions réservées à la génération de nouvelles données'},
        {'name': 'training', 'description': 'Fonctions réservées l entrainement de modèles'},
        {'name': 'sentiment_analysis', 'description': 'Fonctions d analyse des sentiments'}
]
)

############# CONFIGURATION DES LOGS  ######################################################## 
# Chemin vers le répertoire du projet
project_root = os.path.abspath(os.path.dirname(__file__))
# Création du répertoire "logs" s'il n'existe pas
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)
# Nom du fichier de logs avec timestamp
log_filename = os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename),
    ]
)
####################################################################################

############# CONFIGURATION DE L'AUTHENTIFICATION  ############################## 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Configuration pour le JWT
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION = 30
####################################################################################

#############     BASE MODELS    ################################################### 
class User(BaseModel):
    username: str
    password: str
    role: List[str]
class UserName(BaseModel):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class Comment(BaseModel):
    comment: str

class Scrapping_Request(BaseModel):
    """ Représente une requête de scrapping.

    Attributes:
        • liste_sites : liste d'enseignes pour lesquelles on va scrapper les pages Trustpilor
        • nbr_pages: nbr de pages
    """
    liste_sites : List
    nbr_pages: Optional[int] = 1
####################################################################################

############# GESTION DE LA "BASE" UTILISATEURS  ############################## 
with open('user_db/users_data.json', 'r') as file:
    users_db = json.load(file)

# Fonction pour écrire les données dans le fichier JSON
def write_users_to_json(users_data):
    with open('user_db/users_data.json', 'w') as file:
        json.dump(users_data, file, indent=2)
####################################################################################
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
    except ExpiredSignatureError:
        raise credentials_exception
    except DecodeError:
        raise credentials_exception
    token_data = TokenData(username=username)
    user = users_db.get(username, None)
    if user is None:
        raise credentials_exception
    return user


# ******************************************************************
# ****************    HOME   ***************************************
# ******************************************************************

@api.get('/', tags=['home'])
async def get_item():
    """Point de terminaison pour vérifier que l'API est bien fonctionnelle 

    Returns :
        dict : message iniquant que l'API fonctionne correctement
    """
    try:
        logging.info("Accès à l'endpoint home")
        return {'message' : 'API fonctionnelle'}
    except Exception as e:
        logging.error(f"Erreur lors de l'accès à l'endpoint home : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne du serveur")


# ******************************************************************
# ****************  HOME  SECURISE  ********************************
# ******************************************************************

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
        logging.info(f"Tentative d'authentification (token) pour l'utilisateur {form_data.username}")
        user = users_db.get(form_data.username)
        if user:
            hashed_password = user.get("hashed_password")
            if not user or not verify_password(form_data.password, hashed_password):
                logging.warning(f"Échec de l'authentification (token) pour l'utilisateur {form_data.username}")
                raise HTTPException(status_code=400, detail="Username ou password incorrect")

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
            access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
            logging.info(f"Authentification réussie (token) pour l'utilisateur {form_data.username}")

            return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logging.error(f"Exception pendant l'authentification (token): {e}")
    
    # Si une exception se produit ou si l'authentification échoue, log + raise HTTPException
    logging.warning(f"Échec de l'authentification (token) pour l'utilisateur {form_data.username}")
    raise HTTPException(status_code=400, detail="Username ou password incorrect")

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

    try:
        logging.info(f"Tentative d'accéder à un endpoint sécurisé par l'utilisateur {current_user['username']}")
        # Votre code existant pour la récupération de données sécurisées

        return {"message": "Accès au endpoint sécurisé avec succès !"}
    except HTTPException as e:
        logging.warning(f"Échec de l'accès à l'endpoint sécurisé par l'utilisateur {current_user['username']}. Raison: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Exception lors de l'accès à l'endpoint sécurisé par l'utilisateur {current_user['username']}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne du serveur")


# ******************************************************************
# ****************  GESTION DES UTILISATEURS  **********************
# ******************************************************************


@api.post('/add_user', tags=['security'])
async def add_user(new_user: User, current_user: str = Depends(get_current_user)):
    """
    Endpoint pour ajouter un nouvel utilisateur. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        new_user (User): Les données de l'utilisateur à ajouter.
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si l'ajout de l'utilisateur a réussi.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires (rôle "admin").
    """

    logging.info(f"Tentative d'ajout d'utilisateur par {current_user['username']}")
    if "admin" not in current_user["role"]:
        logging.warning(f"Tentative d'ajout d'utilisateur par un utilisateur non autorisé ({current_user['username']})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission refusée. Seul un administrateur peut ajouter un utilisateur",
        )
    else : 
        # Vérifier si l'utilisateur existe déjà
        if new_user.username in users_db:
            logging.warning(f"Tentative d'ajout d'un utilisateur déjà existant ({new_user.username})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'utilisateur avec le nom {new_user.username} existe déjà.",
            )
        # Hasher le mot de passe
        hashed_password = pwd_context.hash(new_user.password)

        # Ajouter l'utilisateur à la base de données
        users_db[new_user.username] = {
            "username": new_user.username,
            "hashed_password": hashed_password,
            "role": new_user.role,
        }
        # Écrire les données mises à jour dans le fichier JSON
        write_users_to_json(users_db)
        logging.info(f"Utilisateur ajouté avec succès: {new_user.username}")
        return {'message': f"Utilisateur ajouté avec succès: {new_user.username}"}



@api.delete('/delete_user', tags=['security'])
async def delete_user(user_to_delete: UserName, current_user: str = Depends(get_current_user)):
    """
    Endpoint pour supprimer un utilisateur. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        username_to_delete (str): Nom de l'utilisateur à supprimer.
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si l'ajout de l'utilisateur a réussi.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires (rôle "admin").
    """
    logging.info(f"Tentative de suppression d'utilisateur par {current_user['username']}")
    
    if "admin" not in current_user["role"]:
        logging.warning(f"Tentative de suppression d'utilisateur par un utilisateur non autorisé ({current_user['username']})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission refusée. Seul un administrateur peut supprimer un utilisateur",
        )

    # Vérifier si l'utilisateur n'existe pas 
    if user_to_delete.username not in users_db:
        logging.warning(f"Tentative de suppression d'un utilisateur non existant ({user_to_delete.username})")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"L'utilisateur avec le nom {user_to_delete.username} n'existe pas.",
        )

    # Supprimer l'utilisateur de la base de données
    del users_db[user_to_delete.username]
    # Écrire les données mises à jour dans le fichier JSON
    write_users_to_json(users_db)
    logging.info(f"Utilisateur ajouté avec succès: {user_to_delete.username}")
    return {'message': f"Utilisateur supprimé avec succès: {user_to_delete.username}"}
    
# ******************************************************************
# ****************    SCRAPPING  / PREPROCESSING *******************
# ******************************************************************

@api.post('/scrap_last30days', tags=['scrapping'])
async def scrap_last30days(scrap_request: Scrapping_Request, current_user: str = Depends(get_current_user)):
    """
    Endpoint pour scrapper. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        scrap_request (Scrapping_Request): Les données de la requete.
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si la création a réussi.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires (rôle "admin").
    """
    logging.info(f"Requête de scrapping reçue de l'utilisateur {current_user['username']}")

    if "admin" not in current_user["role"]:
        logging.warning(f"Tentative non autorisée de scrapping par l'utilisateur {current_user['username']}")
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

    logging.info(f"Longueur du DataFrame : {len(df)}")

    # Save the DataFrame to CSV
    df.to_csv(csv_filepath, sep=';', quotechar='"', index=False)
    logging.info(f"Données écrites dans : {csv_filepath}, {str(len(df))} lignes")
    return {'message': f"Data written to: {csv_filepath} {str(len(df))} rows" }



@api.post('/process_comments', tags=['data management'])
async def process_comments(current_user: str = Depends(get_current_user)):
    """
    Endpoint pour processer les commentaires scrappés. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

    Args:
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        dict: Un message indiquant si le data processing a réussi.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires (rôle "admin").

    """
    logging.info(f"Requête de processing reçue de l'utilisateur {current_user['username']}")
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
    logging.info(f"Chemin du répertoire des données externes : {external_data_path}")

    # Vérifier l'existence du répertoire
    if not os.path.exists(external_data_path) or not os.path.isdir(external_data_path):
        logging.error(f"Le répertoire {external_data_path} n'existe pas.")
        exit()
    # Vérifier l'existence du fichier
    if not os.path.exists(csv_filepath_input) or not os.path.isfile(csv_filepath_input):
        logging.error(f"Le fichier {csv_filepath_input} n'existe pas.")
        exit()

    # Le répertoire et le fichier existent, poursuivre avec le reste du code
    logging.info(f"Le répertoire {external_data_path} et le fichier {csv_filepath_input} existent.")


    # Nom du CSV où les données seront écrites
    csv_filename_output = 'scrapped_comments_processed.csv'
    # Répertoire de données depuis le répertoire src
    interim_data_path = os.path.join( '..', 'data', 'interim')
    # Si le répertoire n'existe pas, on le crée
    os.makedirs(interim_data_path, exist_ok=True)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath_output = os.path.join(interim_data_path, csv_filename_output)
    
    df = Process_Comments.Process_Comments_Notes(csv_filepath_input)

    df.to_csv(csv_filepath_output, sep=';', quotechar='"', index=False)
    logging.info(f"Données écrites dans : {csv_filepath_output}, {str(len(df))} lignes")
    
    return {'message': f"Data written to: {csv_filepath_output} {str(len(df))} rows" }




# @api.post('/histo_process_comments', tags=['data management'])
# async def histo_process_comments(current_user: str = Depends(get_current_user)):
#     """
#     Endpoint pour historiser les commentaires scrappés. Seuls les utilisateurs avec le rôle d'administrateur peuvent l'utiliser.

#     Args:
#         current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

#     Returns:
#         dict: Un message indiquant si le data processing a réussi.
#     """
#     if "admin" not in current_user["role"]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Permission refusée. Seul un administrateur peut historiser des données",
#         )

#     # Nom du CSV où les données à historiser sont lues
#     csv_filename_input = 'scrapped_comments_processed.csv'
#     # Répertoire de données depuis le répertoire src
#     interim_data_path = os.path.join( '..', 'data', 'interim')
#     print("interim_data_path : ",interim_data_path)
#     # Construit le chemin complet pour atteindre le csv
#     csv_filepath_input = os.path.join(interim_data_path, csv_filename_input)
#     print("csv_filepath_input : ", csv_filepath_input)
#     # Vérifier l'existence du répertoire
#     if not os.path.exists(interim_data_path) or not os.path.isdir(interim_data_path):
#         print(f"Le répertoire {interim_data_path} n'existe pas.")
#         exit()
#     # Vérifier l'existence du fichier
#     if not os.path.exists(csv_filepath_input) or not os.path.isfile(csv_filepath_input):
#         print(f"Le fichier {csv_filepath_input} n'existe pas.")
#         exit()
#     # Le répertoire et le fichier existent, poursuivre avec le reste du code
#     print(f"Le répertoire {interim_data_path} et le fichier {csv_filepath_input} existent.")

#     # Nom du CSV où les données déjà historisées sont lues puis réécrites après ajout des nouvelles données
#     csv_filename_histo = 'processed_comments_histo.csv'
#     # Répertoire de données depuis le répertoire src
#     processed_data_path = os.path.join( '..', 'data', 'processed')
#     print("processed_data_path : ",processed_data_path)
#     # Construit le chemin complet pour atteindre le csv
#     csv_filepath_histo = os.path.join(processed_data_path, csv_filename_histo)
#     print("csv_filepath_histo : ", csv_filepath_histo)
#     # Vérifier l'existence du répertoire
#     if not os.path.exists(processed_data_path) or not os.path.isdir(processed_data_path):
#         print(f"Le répertoire {processed_data_path} n'existe pas.")
#         exit()
#     # Vérifier l'existence du fichier
#     if not os.path.exists(csv_filepath_histo) or not os.path.isfile(csv_filepath_histo):
#         print(f"Le fichier {csv_filepath_histo} n'existe pas.")
#         exit()

#     # Le répertoire et le fichier existent, poursuivre avec le reste du code
#     print(f"Le répertoire {processed_data_path} et le fichier {csv_filepath_histo} existent.")

#     result_dico = Process_Comments.Histo_New_Comments(csv_filepath_input,csv_filepath_histo)
#     df_result = result_dico['df_result']
#     df_result.to_csv(csv_filepath_histo, sep=';', quotechar='"', index=False)
#     print (result_dico['nb_rows_input'], result_dico['nb_rows_histo'], result_dico['nb_rows_added_to_histo'], len(df_result))

#     return {'message': f"Data written to: {csv_filepath_histo} : {str(result_dico['nb_rows_added_to_histo'])} rows added to {str(result_dico['nb_rows_histo'])} in histo : {str(len(df_result))} in total"}


    
# ******************************************************************
# ****************        PREDICTION             *******************
# ******************************************************************


@api.post('/prediction', tags=['sentiment_analysis'])
async def prediction(comment: Comment, current_user: str = Depends(get_current_user)):
    """
    Endpoint pour prédire. Seuls les utilisateurs avec le rôle d'utilisateur peuvent l'utiliser.

    Args:
        comment (str): Commentaire
        current_user (str): Nom de l'utilisateur actuel obtenu à partir des informations d'authentification.

    Returns:
        Un dictionnaire contenant :
            - la prédiction de classe (0 ou 1 si la prédiction a fonctionné, -1 sinon)
            - les probabilités pour 0 et 1 (liste)
            - et un message de statut.
                - Si la prédiction est réussie, le message indique que la prédiction est fonctionnelle.
                - Si le vectorizer ou le modèle est introuvable, le message indique l'erreur recontrée.
                - En cas d'erreur inattendue, un message d'erreur général est renvoyé.
 
    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires (rôle "user").

    """
    logging.info(f"Requête de prédiction reçue de l'utilisateur {current_user['username']}")

    if "user" not in current_user["role"]:
        logging.warning(f"Tentative non autorisée de prédiction par l'utilisateur (non user) {current_user['username']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission refusée. Seul un utilisateur peut réaliser une prédiction",
        )
    logging.info(f"Commentaire à prédire : {comment.comment}")
    try:
        result_dict= Predict_Sentiments.Predict_Sentiments_DTC(comment.comment)
        logging.info(f"Prédiction réussie. Résultat : {result_dict}")
        return result_dict
    except Exception as e:
        logging.exception(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la prédiction. Vérifiez les logs pour plus d'informations.",
        )


