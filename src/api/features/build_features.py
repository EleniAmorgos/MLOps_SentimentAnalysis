
import pandas as pd
import numpy as np
from time import time
import tqdm
# chargement de la bibliothèque de stopwords et de tokenisation
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.tokenize.regexp import RegexpTokenizer
from nltk.tokenize import PunktSentenceTokenizer

from urllib.parse import urlsplit


class Process_Comments():
    @staticmethod
    def commentaire_filtering(txt, stop_words):
        new_txt = ""
        tokenizer = RegexpTokenizer("[a-zA-Zéèëãñ\']{3,}")
        tokens = tokenizer.tokenize(txt.lower())
        for word in tokens:
            if word not in stop_words:
                new_txt += str(word) + " "
        return new_txt


    @staticmethod
    def Process_Comments_Notes(csv_filepath_input):

        df = pd.read_csv(csv_filepath_input,  sep=';', quotechar='"')
        # print(df.head(10))
        print(df.columns)
        print(len(df) , 'lignes dans le fichier en input')
        df = df[df['commentaire'].isna()==False]
        print(len(df) , 'lignes conservées dans le fichier en output (comentaire non Nan)')


        # chargement des listes stopwords pour les 3 langues principales 
        stop_words_french = stopwords.words('french')
        stop_words_english = stopwords.words('english')
        stop_words_spanish = stopwords.words('spanish')
        # création d'une stopwords regroupant les 3 langues
        stop_words = stop_words_french + stop_words_english + stop_words_spanish



        # màj colonne commentaire par application de la fonction commentaire_filtering à la colonne commentaire
        df['commentaire'] = df['commentaire'].apply(lambda x : Process_Comments.commentaire_filtering(str(x), stop_words))
        print(df['note'].value_counts())

        return (df)
    

    @staticmethod
    def Histo_New_Comments(csv_filepath_input, csv_filepath_histo):
        # Df contenant les données du csv des nouveaux commentaires scrappés et processés
        df_input = pd.read_csv(csv_filepath_input, sep=';', quotechar='"')
        # Df contenant l'historique des commentaires scrappés et processés
        df_histo = pd.read_csv(csv_filepath_histo, sep=';', quotechar='"')

        df_histo_initial_columns=df_histo.columns.to_list()
        print("df_histo_initial_columns : ", df_histo_initial_columns)

        df_input['date_day'] = pd.to_datetime(df_input['date']).dt.strftime('%Y%m%d')
        df_histo['date_day'] = pd.to_datetime(df_histo['date']).dt.strftime('%Y%m%d')
        
        print ("df_input : " , len(df_input))
        print ("df_input.columns : " , df_input.columns)
        print ("df_histo : " , len(df_histo))
        # Compte le nombre de lignes par source x jour dans df_input
        result_count_input = df_input.groupby(['site', 'date_day']).size().reset_index(name='row_count')
        result_count_input = result_count_input.sort_values(by=['site', 'date_day'])
        
        # Compte le nombre de lignes par source x jour dans df_result
        result_count_histo = df_histo.groupby(['site', 'date_day']).size().reset_index(name='row_count')
        result_count_histo = result_count_histo.sort_values(by=['site', 'date_day'])
        print("result_count_histo.columns :" , result_count_histo.columns)

        # ajoute à df_input les colonnes de result_count_histo (left join)
        # si ces colonnes sont vides, il n'y a donc pas de correspondance source x jour dans df_histo
        merged_df = pd.merge(df_input, result_count_histo, on=['site', 'date_day'], how='left', suffixes=('_input', '_count'))
        print("merged_df.columns : " , merged_df.columns)
        print("merged_df : " , len (merged_df))

        # Filtre les lignes sans correspondances ds l'histo = "nouveaux" commentaires
        df_input_rows_with_no_match = merged_df[merged_df['row_count'].isnull()].reset_index(drop=True)
        print("df_input_rows_with_no_match", len (df_input_rows_with_no_match))
         
        max_id = max(df_histo["id"]) if len(df_histo)>0 else 0
        df_input_rows_with_no_match["id"] = df_input_rows_with_no_match.index + max_id + 1

        df_result = pd.concat([df_histo[df_histo_initial_columns] , df_input_rows_with_no_match[df_histo_initial_columns] ])
        print("df_result", len (df_result))

        return { 'df_result' : df_result ,
                 'nb_rows_input' : len(df_input),
                 'nb_rows_histo' : len(df_histo),
                 'nb_rows_added_to_histo' : len (df_input_rows_with_no_match)
                }
