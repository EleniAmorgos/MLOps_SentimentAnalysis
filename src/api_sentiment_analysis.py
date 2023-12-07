from fastapi import FastAPI, HTTPException,status,Depends, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
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

from data.web_scrapping import WebScrapping_RatedComments

api = FastAPI(
    title="API Sentiment analysis",
    description="API permettant l'analyse de sentiments depuis un texte",
    version="1.0.1",
    openapi_tags=[
        {'name': 'home', 'description': 'Fonctions de base'},
        {'name': 'sentiment_analysis', 'description': 'Fonctions d analyse des sentiments'},
        {'name': 'scrapping', 'description': 'Fonctions réservées à la génération de nouvelles données'},
        {'name': 'training', 'description': 'Fonctions réservées l entrainement de modèles'}
]
)
# Dictionnaire des utilisateurs
users = {
    "alice": {"password": "wonderland", "role": ["user"]},
    "bob": {"password": "builder", "role": ["user"]},
    "clementine": {"password": "mandarine", "role": ["user"]},
    "admin": {"password": "TFH_dstMLOPS23", "role": ["user", "admin"]}
}


class Scrapping_Request(BaseModel):
    """ Représente une requête de scrapping.

    Attributes:
        • url: url à scrapper
        • nbr_pages: nbr de pages
    """
    url: str
    nbr_pages: Optional[int] = 1


def load_csv():
    """ Charge le fichier et renvoie les lignes (commentaires) sous forme de liste de dictionnaires
    """
    with open(csv_name,'r',encoding='utf8') as question_file:
        return list(csv.DictReader(question_file))

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """  Valide les identifiants encodés de l'utilisateur
    """
    user_data = users.get(credentials.username)
    if user_data is None or user_data["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": credentials.username, "role": user_data["role"]}

@api.get('/', tags=['home'])
async def get_item():
    """Point de terminaison pour vérifier que l'API est bien fonctionnelle 

    Returns :
        dict : message iniquant que l'API fonctionne correctement
    """
    return {'message' : 'API fonctionnelle'}


@api.post('/scrap_last30days', tags=['administration'])
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
        'url': scrap_request.url ,
        'nbr_pages': scrap_request.nbr_pages
    }
    
    # Nom du CSV où les données seront écrites
    csv_filename = 'cdiscount_last30days.csv'
    # Répertoire de données depuis le répertoire src
    external_data_path = os.path.join( '..', 'data', 'external')
    # print(external_data_path)
    # Si le répertoire n'existe pas, on le crée
    os.makedirs(external_data_path, exist_ok=True)
    # Construit le chemin complet pour atteindre le csv
    csv_filepath = os.path.join(external_data_path, csv_filename)
    print(csv_filepath)

    df = WebScrapping_RatedComments.WebScrapping_Comments(url_to_scrap=scrap_request_dict['url'], nbr_pages = scrap_request_dict['nbr_pages'])

    print("Longueur du df : ", len(df))
    print(df.head(10))
    print(df.tail(10))

    # Save the DataFrame to CSV
    df.to_csv(csv_filepath, sep=';', quotechar='"', index=False)

    return {'message': f"Data written to: {csv_filepath} {str(len(df))} rows" }
