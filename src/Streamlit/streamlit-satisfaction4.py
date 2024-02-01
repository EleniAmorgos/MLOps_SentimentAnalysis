# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 00:30:02 2023

@author: t.fourtouill
"""

import streamlit as st
from PIL import Image
import requests

# DEFINITION DES FONCTIONS : il faudra remplacer l'IP par le nom du container qui contient l'api
# et le port par le port exposé par l'api

url = "http://api:8001/"

def call_api(url):
    headers = {'accept': 'application/json'}

    response_call = requests.get(url, headers=headers).json()
    return response_call

def token_api(url, username, password):
    url_token = url + f"token"
    params = {
        'username': username,
        'password': password,
        },
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    token = requests.get(url_token, params=params, headers=headers)
    return token

def scrap_api(url, sites, nbr_pages, token):
    url_scrap = url +f"scrap_last30days"
    params = {
        'liste_sites':sites,
        'nbr_pages': int(nbr_pages)
        },
    headers = {
    'accept': 'application/json',
    'Authorization': token
    }
    
    response_scrap = requests.get(url_scrap, params=params, headers=headers)
    return response_scrap

def preprocess_scrap_api(url, response_scrap, token):
    url_preprocess = url + f"process_comments"
    headers = {
    'accept': 'application/json',
    'Authorization': token
    }

    response_preprocess = requests.get(url_preprocess, headers=headers)
    return response_preprocess

def sentiment_api(url, comment, token):
    url_predict = url + f"pred_comment"
    headers = {
    'accept': 'application/json',
    'Authorization': token
    }

    response_sentiment = requests.get(url_predict, comment, headers=headers)
    return response_sentiment


# INSTANCIATION DE L'OBJET STREAMLIT, APPLICATION DU STYLE

st.set_page_config(layout="wide", page_title="Satisfaction Client")
with open('images/style.css') as f: 
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 

# INFORMATIONS GENERALES

image_poing = Image.open("images/OIP.png")
st.sidebar.image(image_poing)
st.sidebar.markdown("Developed by Thomas FOURTOUILL using [Streamlit](https://www.streamlit.io)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.2")


# CHARGEMENT DES LIBRAIRIES

import pandas as pd
from pathlib import Path
import numpy as np

import pickle

pd.options.display.max_colwidth=800
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)


# INSTANCIATON DES PAGES (ICI 2 PAGES)

page = st.sidebar.radio(label='page n°', options=[1, 2])


# PAGE 1

# PRESENTATION

if page==1:
    
    st.title("Projet satisfaction clients")
    st.markdown(""" 
                l'objectif est de prédire le sentiment positif ou négatif à attribuer à un commentaire
                """) 


# TEST API

    if st.button("Vérifier réponse de l'API"):
        response_call = call_api(url)
    
        st.write(response_call)    
   
# TOKEN

    # Utilisation de la variable de session pour `token`
    if 'token' not in st.session_state:
        st.session_state['token'] = ''

    # identification pour récupération du token
    st.markdown(""" veuillez saisir vos identifiants de connexion pour obtenir votre token""")

    user_id = st.text_input("saisissez votre identiant :")
    passe_id = st.text_input("saisissez votre mot de passe :")
   
    if st.button("Générer un token"):
        response_token = token_api(url, user_id, passe_id)
        st.session_state['token'] = response_token
        
        st.write('Voici votre token : ', st.session_state['token'])


# SCRAPPING

    sites = st.multiselect(
    'Choisissez les sites à scrapper',
    ['ubaldi.com', 'habitatetjardin.com', 'menzzo.fr', 'fnac.com', 'darty.com', 'temu.com', 'cdiscount.com']
    )

    st.write('You selected:', sites)
        
    nbr_pages = st.text_input("saisissez le nombre de pages à scrapper :")
    
    if st.button("Scrapper les données"):
        response_scrap = scrap_api(url, sites, nbr_pages, st.session_state['token'])
        st.session_state['scrap'] = response_scrap
        
        st.json(response_scrap)


# PREPROCESSING
    
    if st.button("Lancer le preprocessing"):
        response_preprocess = preprocess_scrap_api(url, response_scrap, st.session_state['token'])
        st.session_state['preprocess'] = response_preprocess
        
        st.json(response_preprocess)


# SAISIE DU COMMENTAIRE

    # saisi du commentaire à prédire
    st.markdown("Merci de saisir le commentaire à prédire")
    
    # saisie du commentaire
    comment = st.text_input("saisir un commentaire :")
    
    # Vectorization du commentaire pour les modèles de Deep Learning
    if st.button("valider le commentaire"):
        with open('comment.txt', 'w') as fichier :
            fichier.write(comment)


# PREDICTIONS

    if st.button("Afficher la prédiction"):
        response_sentiment = sentiment_api(comment, st.session_state['token'])
    
        st.write(response_sentiment)


# PAGE 2

# DOCUMENTATION

elif page==2:
    st.title("Documentation du projet")
    st.markdown(""" 
                Ci-dessous vous trouverez la documentation qui a été présentée lors du projet
                """)  
    
    with open("documentation/documentation.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(label="Download PDF Tutorial", 
        data=PDFbyte,
        file_name="documentation.pdf",
        mime='application/octet-stream')
    
    st.title("Evaluation du modèle utilisé")
    st.markdown(""" 
                Ci-dessous les caractéristique de l'évaluation du modèle utilisé
                """) 
    

# EVALUATION DU MODELE

    liste = open('predictions/model_evaluation.txt', 'rb')
    model_evaluation = pickle.load(liste)
    st.write('loss (perte):', round(model_evaluation[0], 2))
    st.write('accuracy (précision):', round(model_evaluation[1], 2))