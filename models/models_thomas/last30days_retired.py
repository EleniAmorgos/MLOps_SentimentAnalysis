# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 21:06:14 2023

@author: t.fourtouill
"""

import pandas as pd

# chargement des donnees retraitees par note
df_retired = pd.read_csv('datasets/SatisfactionClients/trustpilot_comment_retired.csv', sep=';')

# chargement des donnees retraitees positive et negative
df_retired_0_1 = pd.read_csv('datasets/SatisfactionClients/trustpilot_comment_retired_0_1.csv', sep=';')

# chargement des donnees des 30 dernier jours
df = pd.read_csv('datasets/SatisfactionClients/last30days.csv', sep=';')

# suppression des colonnes site et date dans les donnees des 30 derniers jours
df.drop(['site', 'date'], axis=1, inplace=True)
df = df[df['commentaire'].isna()==False]

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
df['new_commentaire'] = df['commentaire'].progress_apply(lambda x : commentaire_filtering(str(x), stop_words))

# suppresion de l ancienne colonne commentaire et rename de la nouvelle
new_df = df.drop(columns=['commentaire']).rename(columns={'new_commentaire' : 'commentaire'})

# ajout des donnees last30days retraitees au donnees globales retraitees note
df_final_retired = df_retired.append(new_df, ignore_index=True)

# enregistrement des donnees retraitees note
df_final_retired.to_csv('datasets/SatisfactionClients/trustpilot_comment_retired.csv', index=False)

# Séparation en 2 : positif et négatif
new_df2 = new_df[new_df['note']!=3]
new_df2['note'] = new_df2['note'].replace([1, 2, 4, 5], [0, 0, 1, 1])

# ajout des donnees last30days retraitees au donnees globales retraitees negatif positif
df_final_retired_0_1 = df_retired_0_1.append(new_df2, ignore_index=True)

# enregistrement des donnees retraitees negatif positif
df_final_retired_0_1.to_csv('datasets/SatisfactionClients/trustpilot_comment_retired_0_1.csv', index=False)