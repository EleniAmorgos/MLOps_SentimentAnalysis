# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 21:06:14 2023

@author: t.fourtouill
"""

import pandas as pd
import numpy as np
import boto3
from io import StringIO
import pickle

import datetime
import os

import sklearn

pd.set_option('mode.chained_assignment', None)

# update de de la base de donnée avec les valeur last30days 
access = pd.read_csv('accessKeys.csv', sep=',')

ACCESS_KEY = access['Access key ID'][0]
SECRET_KEY = access['Secret access key'][0]
region_name =  'eu-west-3'

bucket_name = 'mlops-comments'

client = boto3.client(
    's3',
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY,
    region_name=region_name
    )


# chargement des donnees retraitees positive et negative
file_retired_0_1 = client.get_object(
            Bucket=bucket_name,
            Key='data/trustpilot_comment_retired_0_1.csv'
            )

body_retired_0_1 = file_retired_0_1['Body']
csv_string_retired_0_1 = body_retired_0_1.read().decode('utf-8')

comment_retired_0_1 = pd.read_csv(StringIO(csv_string_retired_0_1), sep=';')

print('les données sont chargées')

# suppression des valeurs manquantes
comment_retired_0_1 = comment_retired_0_1[comment_retired_0_1['commentaire'].isna()==False]

# suppression des valeurs neutres note=3
comment_retired_0_1 = comment_retired_0_1[comment_retired_0_1['commentaire']!=3]

# séparation de la variable cible et des variables explicatives
X = comment_retired_0_1['commentaire']
y = comment_retired_0_1['note']

# transformation des notes 1 et 2 en 0 (sentiment négatif) et 4 et 5 en 1 (sentiment positif)
y = y.replace({'1' : '0', '2' : '0', '4' : '1', '5' : '1'})

print('les données sont préprocessées')

print('Entrainement du modèle')

# séparation du jeu de données en un dataset d'entrainement et un dataset de test
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# conversion des chaines de caratères en tokens numériques
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(max_features=5000, decode_error="replace")

vectorizer_fit = vectorizer.fit(X_train)

X_train = vectorizer.fit_transform(X_train).todense()
X_test = vectorizer.transform(X_test).todense()

# X_train = np.asarray(X_train)
# X_test = np.asarray(X_test)

#Save vectorizer.vocabulary_
pickle.dump(vectorizer.vocabulary_, open("vec_vocab_dtc.pkl","wb"))

#Save vectorizer
pickle.dump(vectorizer_fit, open("vect_dtc.pkl","wb"))

print('le vectorizer est enregistré')

# calcul du model
from sklearn.tree import DecisionTreeClassifier

clf = DecisionTreeClassifier(max_depth=10)

clf.fit(X_train, y_train)

# enregistrement des donnees retraitees negatif positif en local dans src 
pickle.dump(clf, open('model_dtc.pkl', 'wb'))

print('le modèle est entrainé et enregistré')

# calcul des prédictions
y_pred = clf.predict(X_test)

model_score_dtc = clf.score(X_test, y_test)

with open('model_score_dtc.txt', 'w') as score:
    score.write(str(model_score_dtc))
    
print('le score du modèle est enregistré')

# # vérification des résultats sur un jeu de test externe (100 commentaires amazon également répartis entre les étoiles)
# df_test_token = vectorizer.transform(df_test['commentaire']).todense()
# y_predict_test = clf.predict(df_test_token)

# #test
# txt = "J'ai réclamé à de nombreuses reprises pour ne pas avoir reçu de modes d'emploi en Français mais Amazon continue à envoyer des produits avec uniquement des modes d'emploi en Anglais ou en chinois. J'ai signalé à la DGCCRF à plusieurs reprises qu'Amazon ne respectait pas la loi française mais ils n'ont rien fait."
# txt = pd.Series(txt)
# txt2 = vectorizer.transform(txt).todense()

# Calcul du temps au début de l'exécution (t0)
date_heure = datetime.datetime.now()
date_heure_str = date_heure.strftime('%Y-%m-%w %H:%M:%S')

# impression du log dans un fichier
if os.environ.get('LOG') == '1':
    with open('logs_model.txt', 'a') as log:
        log.write("la vectorization, le model et le score ont bien été enregistés le : {}".format(date_heure_str))
