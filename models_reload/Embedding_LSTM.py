# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 12:30:02 2023

@author: t.fourtouill
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from time import time
import itertools
import keras
import tensorflow
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

df = pd.read_csv('datasets/SatisfactionClients/trustpilot_comment_retired.csv')
df = df[df['commentaire'].isna()==False]

# séparation de la variable cible et des variables explicatives
X = df['commentaire']
y = df['note'].values

# séparation du jeu de données en un dataset d'entrainement et un dataset de test
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# tokenisation des commentaires
num_words=5000
tk = Tokenizer(num_words=num_words, lower=True)

# entrainement de la tokenisation sur le X_train
tk.fit_on_texts(X_train)

# nb de ligne de la matrice
word_index = tk.word_index

# nb de colonnes dans la matrice
vocabulary_size = tk.num_words

# mise sous vecteur des commentaires
X_seq_train = tk.texts_to_sequences(X_train)
X_seq_test = tk.texts_to_sequences(X_test)

# transformation en matrice de même longueur par maxlen défini ci-dessous. Avec des 0 si colonne inférieure à maxlen
max_words = 130
X_pad_train = pad_sequences(X_seq_train, maxlen=max_words, padding='post')
X_pad_test= pad_sequences(X_seq_test, maxlen=max_words, padding='post')

# Création des couches du modéle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling1D, Input, Embedding, Dropout, LSTM

embedding_size = 32

model_embedding_1 = Sequential()
model_embedding_1.add(Embedding(input_dim=vocabulary_size, output_dim=embedding_size, input_length=max_words, embeddings_initializer='uniform'))  # On reprend le nb de mot choisi dans la tokenisation
model_embedding_1.add(LSTM(200)) 
model_embedding_1.add(Dense(units=6, activation='softmax')) # En sortie le nb de units devra correspondre aux nb de variables cibles

# timer pour mesurer le temps écoulé entre les epochs de début et de fin de callback
from tensorflow.keras.callbacks import Callback
from timeit import default_timer as timer

class TimingCallback(Callback):
    def __init__(self, logs={}):
        self.logs=[]
    def on_epoch_begin(self, epoch, logs={}):
        self.starttime = timer()
    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(timer()-self.starttime)

# instanciation la fonction TimingCallback()
time_callback = TimingCallback()

# Création des callback
from tensorflow.keras.callbacks import EarlyStopping

early_stop = EarlyStopping(monitor='val_loss',
                          min_delta=0.01,
                          patience=3,
                          mode='min',
                          restore_best_weights=True,
                          verbose=1)


model_embedding_1.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


batch_size = 32
epochs = 10
history = model_embedding_1.fit(X_pad_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1,
                               callbacks=[early_stop, time_callback])

# enregistrement du modele
import os
path = "/Users/t.fourtouill/Downloads/SatisfactionClients"
os.makedirs(path, exist_ok=True)
model_embedding_1.save('datasets/SatisfactionClients/model_embedding_lstm')

# evaluation du modele : liste avec la loss et l accuracy
evaluation_model_lstm = model_embedding_1.evaluate(X_pad_test, y_test, verbose=1)


# CALCUL DES PREDICTIONS

# chargement d un test amazon avec 100 notes egalement reparties
df_test = pd.read_csv('datasets/SatisfactionClients/amazon_test1.csv')

# création des prédictions du eu de test cdiscount à partir du modèle
predict_cdiscount = model_embedding_1.predict(X_pad_test, verbose=1)
predict_cdiscount_class = predict_cdiscount.argmax(axis=1)

# séparation de la variable cible et des variables explicatives
check_set = df_test['commentaire'].values

# vectorisation des token
check_seq = tk.texts_to_sequences(check_set)

# mise sous matrice numpy
check_pad = pad_sequences(check_seq, maxlen=max_words, padding='post')

# création des prédictions du jeu de test amazon à partir du modèle
check_predict = model_embedding_1.predict(check_pad, verbose=1)

# mise au format des predictions
check_predict_class = check_predict.argmax(axis=1)

# diagramme baton des predictions du test
fig = sns.countplot(check_predict_class)
fig.savefig('predictions_lmst.png')

# comparaison des prédictions et des notes du jeu de test
check_df_lmst = pd.DataFrame(list(zip(df_test.commentaire, df_test.note, check_predict_class)), columns=['commentaire', 'note', 'prediction'])


from sklearn.metrics import classification_report

cr_lmst = classification_report(y_test, predict_cdiscount_class)
cm_lmst = pd.crosstab(y_test, predict_cdiscount_class, rownames=['données réelles'], colnames=['predictions'])

# vérification des résultats sur un jeu de test externe (100 commentaires amazon également répartis entre les étoiles)
cm_test_lmst = classification_report(df_test.note, check_predict_class)
cm_test2_lmst = pd.crosstab(df_test.note, check_predict_class, rownames=['données réelles'], colnames=['predictions'])
cm_test3_lmst = pd.crosstab(df_test.note, check_predict_class, rownames=['données réelles'], colnames=['predictions'], normalize=0)








