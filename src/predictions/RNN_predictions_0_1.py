# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 00:30:02 2023

@author: t.fourtouill
"""

from pathlib import Path
import numpy as np

import tensorflow as tf
import keras

from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.models import load_model
import pickle

# Vectorization du commentaire pour les modèles de Deep Learning
# comment CORRESPOND AU COMMENTAIRE SAISI PAR L UTILISATEUR. VOIR COMMENT ON LE RECUPERE
comment_DL = [comment]
# num_words = 5000

# chargement du tokenizer qui à servi pour l'entrainement
with open('datasets/SatisfactionClients/Matrices/tokenizer.pkl', 'rb') as handle:
    tk = pickle.load(handle)

check_seq_0_1 = tk.texts_to_sequences(comment_DL) 

# mise sous matrice numpy
max_words = 130
check_pad_0_1 = pad_sequences(check_seq_0_1, maxlen=max_words, padding='post')

model = tf.keras.models.load_model('C:/Users/t.fourtouill/Bureau/streamlit_satisfaction_clients2/models/model_0_1_embedding8')
check_predict_0_1 = model.predict(check_pad_0_1, verbose=1)
check_predict_class_0_1 = check_predict_0_1.argmax(axis=1)
if check_predict_class_0_1==0:
    prediction = 'le commentaire est négatif'
else:
    prediction = 'le commentaire est postif'