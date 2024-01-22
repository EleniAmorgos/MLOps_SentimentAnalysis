# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 21:06:14 2023

@author: t.fourtouill
"""

import pandas as pd
import boto3
from io import StringIO

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

# chargement des donnees retraitees par note
file_retired = client.get_object(
            Bucket=bucket_name,
            Key='data/trustpilot_comment_retired.csv'
            )

body_retired = file_retired['Body']
csv_string_retired = body_retired.read().decode('utf-8')

comment_retired = pd.read_csv(StringIO(csv_string_retired), sep=';', dtype={'commentaire':str})


# chargement des donnees retraitees positive et negative
file_retired_0_1 = client.get_object(
            Bucket=bucket_name,
            Key='data/trustpilot_comment_retired_0_1.csv'
            )

body_retired_0_1 = file_retired_0_1['Body']
csv_string_retired_0_1 = body_retired_0_1.read().decode('utf-8')

comment_retired_0_1 = pd.read_csv(StringIO(csv_string_retired_0_1), sep=';')

# chargement des donnees des 30 dernier jours
file_last30days = client.get_object(
            Bucket=bucket_name,
            Key='data/last30days.csv'
            )

body_last30days = file_last30days['Body']
csv_string_last30days = body_last30days.read().decode('utf-8')

comment_last30days = pd.read_csv(StringIO(csv_string_last30days), sep=';')

# suppression des colonnes site et date dans les donnees des 30 derniers jours
comment_last30days.drop(['site', 'date'], axis=1, inplace=True)
comment_last30days = comment_last30days[comment_last30days['commentaire'].isna()==False]

# chargement de la bibliothèque de stopwords et de tokenisation
from nltk.corpus import stopwords
from nltk.tokenize.regexp import RegexpTokenizer

import nltk
nltk.download('punkt')

# chargement des listes stopwords pour les 3 langues principales 
stop_words_french = stopwords.words('french')
stop_words_english = stopwords.words('english')
stop_words_spanish = stopwords.words('spanish')

# création d'une stopwords regroupant les 3 langues
stop_words = stop_words_french + stop_words_english + stop_words_spanish

# creation d une fonction qui nettoie les datas pour utilisation dans les modeles
def commentaire_filtering(txt, stop_words):
    new_txt = ""
    tokenizer = RegexpTokenizer("[a-zA-Zéèëãñ\']{3,}")
    tokens = tokenizer.tokenize(txt.lower())
    for word in tokens:
        if word not in stop_words:
            new_txt += str(word) + " "
    return new_txt

# application de la fonction aux datas
comment_last30days['new_commentaire'] = comment_last30days['commentaire'].apply(lambda x : commentaire_filtering(str(x), stop_words))

# suppresion de l ancienne colonne commentaire et rename de la nouvelle
new_comment_last30days = comment_last30days.drop(columns=['commentaire']).rename(columns={'new_commentaire' : 'commentaire'})

# ajout des donnees last30days retraitees au donnees globales retraitees note
new_comment_retired = pd.concat([comment_retired, new_comment_last30days], axis=0, ignore_index=True)

# enregistrement des donnees retraitees note
new_comment_retired.to_csv('base_retired.csv', sep=';', index=False)
client.upload_file(Filename='base_retired.csv', Bucket=bucket_name, Key=('data/trustpilot_comment_retired.csv'))

# Séparation en 2 : positif et négatif
new_comment_last30days_0_1 = new_comment_last30days[new_comment_last30days['note']!=3]
new_comment_last30days_0_1['note'] = new_comment_last30days_0_1['note'].replace([1, 2, 4, 5], [0, 0, 1, 1])

# ajout des donnees last30days retraitees au donnees globales retraitees negatif positif
new_comment_retired_0_1 = pd.concat([comment_retired_0_1, new_comment_last30days_0_1], axis=0, ignore_index=True)

# enregistrement des donnees retraitees negatif positif
new_comment_retired_0_1.to_csv('base_retired_0_1.csv', sep=';', index=False)
client.upload_file(Filename='base_retired_0_1.csv', Bucket=bucket_name, Key=('data/trustpilot_comment_retired_0_1.csv'))
