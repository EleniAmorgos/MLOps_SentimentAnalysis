# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 00:30:02 2023

@author: t.fourtouill
"""

import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_title="Satisfaction Client")
with open('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/style.css') as f: 
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 

image_poing = Image.open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/images/OIP.png")
st.sidebar.image(image_poing)
st.sidebar.markdown("Developed by Thomas FOURTOUILL using [Streamlit](https://www.streamlit.io)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.2")

import pandas as pd
from pathlib import Path
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import tensorflow as tf
import keras

from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.models import load_model
from joblib import dump, load
import pickle

pd.options.display.max_colwidth=800
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

# instanciation des pages ici 2
page = st.sidebar.radio(label='page n°', options=[1, 2])

# contenu de la 1ère page
if page==1:
    
    st.title("Projet satisfaction clients")
    st.markdown(""" 
                l'objectif est de prédire le sentiment positif ou négatif à attribuer à un commentaire
                """) 
   
    st.markdown("Merci de saisir le commentaire à prédire")
    
    # saisie du commentaire
    comment = st.text_input("saisir un commentaire :")
    
    # Vectorization du commentaire pour les modèles de Deep Learning
    comment_DL = [comment]
    
    with open('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/tokenizer/tokenizer.pkl', 'rb') as handle:
        tk = pickle.load(handle)
    
    tk.fit_on_texts(comment_DL)
    check_seq = tk.texts_to_sequences(comment_DL)
    
    # # mise sous matrice numpy
    max_words = 130
    check_pad = pad_sequences(check_seq, maxlen=max_words, padding='post')
                
    model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/model/model_rnn_0_1')
    check_predict = model.predict(check_pad, verbose=1)
    check_predict_class = check_predict.argmax(axis=1)
    if check_predict_class==0:
        st.write('le commentaire est négatif')
    else:
        st.write('le commentaire est postif')
  
# contenu de la 2ème page
elif page==2:
    st.title("Documentation du projet")
    st.markdown(""" 
                Ci-dessous vous trouverez la documentation qui a été présentée lors du projet
                """)  
    
    with open("C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/documentation.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(label="Download PDF Tutorial", 
        data=PDFbyte,
        file_name="documentation.pdf",
        mime='application/octet-stream')
    
    st.title("Evaluation du modèle utilisé")
    st.markdown(""" 
                Ci-dessous les caractéristique de l'évaluation du modèle utilisé
                """) 
    
    # Récupère ta liste
    liste = open('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/predictions/model_evaluation.txt', 'rb')
    model_evaluation = pickle.load(liste)
    st.write('loss (perte):', round(model_evaluation[0], 2))
    st.write('accuracy (précision):', round(model_evaluation[1], 2))