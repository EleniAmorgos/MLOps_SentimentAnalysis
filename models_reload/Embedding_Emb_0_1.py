# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 21:02:20 2023

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

df_0_1 = pd.read_csv('datasets/SatisfactionClients/trustpilot_comment_retired_0_1.csv')
df_0_1 = df_0_1[df_0_1['commentaire'].isna()==False]
df_0_1 = df_0_1[df_0_1['note']!=3]
df_0_1['note'] = df_0_1['note'].replace({'1' : '0', '2' : '0', '4' : '1', '5' : '1'})

# séparation de la variable cible et des variables explicatives
X1 = df_0_1['commentaire']
y1 = df_0_1['note']

# séparation du jeu de données en un dataset d'entrainement et un dataset de test
from sklearn.model_selection import train_test_split
X_train1, X_test1, y_train1, y_test1 = train_test_split(X1, y1, test_size=0.2, shuffle=True)

# tokenisation des commentaires
num_words=5000
tk = Tokenizer(num_words=num_words, lower=True)

# entrainement de la tokenisation sur le X_train
tk.fit_on_texts(X_train1)

# nb de ligne de la matrice
word_index = tk.word_index

# nb de colonnes dans la matrice
vocabulary_size = tk.num_words

# mise sous vecteur des commentaires
X_seq_train1 = tk.texts_to_sequences(X_train1)
X_seq_test1 = tk.texts_to_sequences(X_test1)

# transformation en matrice de même longueur par maxlen défini ci-dessous. Avec des 0 si colonne inférieure à maxlen
max_words = 130
X_pad_train1 = pad_sequences(X_seq_train1, maxlen=max_words, padding='post')
X_pad_test1 = pad_sequences(X_seq_test1, maxlen=max_words, padding='post')

# Création des couches du modéle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling1D, Input, Embedding, Dropout

embedding_size = 100

model_0_1_embedding_1 = Sequential()
model_0_1_embedding_1.add(Embedding(input_dim=vocabulary_size, output_dim=embedding_size, input_length=max_words, embeddings_initializer='uniform'))  # On reprend le nb de mot choisi dans la tokenisation
model_0_1_embedding_1.add(GlobalAveragePooling1D())
model_0_1_embedding_1.add(Dense(units=256, activation='relu'))
model_0_1_embedding_1.add(Dropout(rate=0.25))
model_0_1_embedding_1.add(Dense(units=128, activation='relu'))
model_0_1_embedding_1.add(Dropout(rate=0.18))
model_0_1_embedding_1.add(Dense(units=64, activation='relu'))
model_0_1_embedding_1.add(Dropout(rate=0.15))
model_0_1_embedding_1.add(Dense(units=32, activation='relu'))
model_0_1_embedding_1.add(Dropout(rate=0.20))
model_0_1_embedding_1.add(Dense(units=1, activation='sigmoid')) # En sortie le nb de units devra correspondre aux nb de variables cibles

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


model_0_1_embedding_1.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


batch_size = 32
epochs = 10
history_0_1 = model_0_1_embedding_1.fit(X_pad_train1, y_train1, batch_size=batch_size, epochs=epochs, validation_split=0.1,
                               callbacks=[early_stop, time_callback])

# enregistrement du modele
import os
path = "/Users/t.fourtouill/Downloads/SatisfactionClients"
os.makedirs(path, exist_ok=True)
model_0_1_embedding_1.save('datasets/SatisfactionClients/model_0_1_embedding_emb')

# evaluation du modele : liste avec la loss et l accuracy
evaluation_model_lstm_0_1 = model_0_1_embedding_1.evaluate(X_pad_test1, y_test1, verbose=1)


# CALCUL DES PREDICTIONS

# chargement d un test amazon avec 100 notes egalement reparties
df_test_0_1 = pd.read_csv('datasets/SatisfactionClients/amazon_test1.csv')
df_test_0_1 = df_test_0_1.drop(columns=['Unnamed: 0'])
df_test_0_1 = df_test_0_1[df_test_0_1['commentaire'].isna()==False]
df_test_0_1 = df_test_0_1[df_test_0_1['note']!=3]
df_test_0_1['note'] = df_test_0_1['note'].replace({1 : 0, 2 : 0, 4 : 1, 5 : 1})

# création des prédictions du eu de test cdiscount à partir du modèle
predict_cdiscount1 = model_0_1_embedding_1.predict(X_pad_test1, verbose=1)
predict_cdiscount_class1 = predict_cdiscount1.round().astype('int').ravel()

# vectorisation des token
check_set_amazon = df_test_0_1['commentaire'].values

# mise sous matrice numpy
check_seq_amazon = tk.texts_to_sequences(check_set_amazon)

# mise sous matrice numpy
check_pad_amazon = pad_sequences(check_seq_amazon, maxlen=max_words, padding='post')

# création des prédictions du jeu de test amazon à partir du modèle
check_predict_0_1 = model_0_1_embedding_1.predict(check_pad_amazon, verbose=1)

# mise au format des predictions
check_predict_0_1_class = check_predict_0_1.round().astype('int').ravel()

# diagramme baton des predictions du test
plt.figure(figsize=(4, 3))
fig_0_1 = sns.countplot(check_predict_0_1_class)
fig_0_1.savefig('predictions_lstm_0_1.png')

# comparaison des prédictions et des notes du jeu de test
check_df_lstm_0_1 = pd.DataFrame(list(zip(df_test_0_1.commentaire, df_test_0_1.note, check_predict_0_1_class)), columns=['commentaire', 'note', 'prediction'])

from sklearn.metrics import classification_report

cm_test1_lstm_0_1 = classification_report(df_test_0_1.note, check_predict_0_1_class)
cm_test2_lstm_0_1 = pd.crosstab(df_test_0_1.note, check_predict_0_1_class, rownames=['données réelles'], colnames=['predictions'])
cm_test3_lstm_0_1 = pd.crosstab(df_test_0_1.note, check_predict_0_1_class, rownames=['données réelles'], colnames=['predictions'], normalize=0)