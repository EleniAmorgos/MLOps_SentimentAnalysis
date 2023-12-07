
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



        # création d'une colonne commentaire_filtre par application de la fonction commentaire_filtering à la colonne commentaire
        df['commentaire_processe'] = df['commentaire'].apply(lambda x : Process_Comments.commentaire_filtering(str(x), stop_words))

        print(df['commentaire_processe'][0])
        print(df['note'].value_counts())

        return (df)
