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
from features.build_features import Process_Comments

api = FastAPI(
    title="API Sentiment analysis",
    description="API permettant l'analyse de sentiments depuis un texte",
    version="1.0.1",
    openapi_tags=[
        {'name': 'home', 'description': 'Fonctions de base'},
        {'name': 'sentiment_analysis', 'description': 'Fonctions d analyse des sentiments'},
        {'name': 'scrapping', 'description': 'Fonctions réservées à la génération de nouvelles données'},
        {'name': 'data management', 'description': 'Fonctions réservées à la génération de nouvelles données'},
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
        'url': scrap_request.url ,
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

    df = WebScrapping_RatedComments.WebScrapping_Comments(url_to_scrap=scrap_request_dict['url'], nbr_pages = scrap_request_dict['nbr_pages'])

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
            detail=f"Permission refusée. Seul un administrateur peut scrapper des données",
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
            detail=f"Permission refusée. Seul un administrateur peut scrapper des données",
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
