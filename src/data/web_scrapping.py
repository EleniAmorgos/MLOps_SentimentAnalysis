import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from time import time

class WebScrapping_RatedComments():
    @staticmethod
    def WebScrapping_Comments(url_to_scrap, nbr_pages):
        html = requests.get(url_to_scrap)
        # transformation de la page en un document exploitable
        # Selon le parsers choisi (html.parser, lxml, lxml-xml, xml, html5lib)
        soup = BeautifulSoup(html.text, 'html.parser')
        # print(soup)
        # Date du commentaire à récupérer
        date_time = soup.find_all('time', {'class' : ""})
        date_time[2]['datetime'][0:19].replace('T', ' ')

        # Récupération du pays du commentaire
        pays = soup.find_all('div', {"class" : "typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua"})
        # Récupération du commentaire
        comment = soup.find_all('p' , {'class' : "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn"})
        print(comment[0].text)
        # Note
        note = soup.find_all('div', {"class" : "styles_reviewHeader__iU9Px"})
        print(note[2]['data-service-review-rating'])

        # Scrapping du commentaire
        #Test de l'URL : 200 si OK, 402, si erreur, 403 si non autorisé par le site
        url_test=url_to_scrap+'&page=2'
        print(requests.get(url_test).status_code)

        # initialisation de l'heure maintenant 
        t0 = time()

        # création de la liste des URL des pages regroupant données pour les 30 derniers jours
        nb_pages = nbr_pages
        liste_url = []
        page = 1

        while page <= nb_pages :
            try :
                url_page=url_to_scrap+'&page='+str(page)
                if requests.get(url_page).status_code==200:
                    liste_url.append(url_page)
            except:
                pass

            page = page + 1

        # scapping des données
        liste_note = []
        liste_commentaire = []
        liste_date = []
        liste_pays = []

        for url_to_scrap in tqdm(liste_url):
            html = requests.get(url_to_scrap)
            soup = BeautifulSoup(html.text, 'html.parser')
            comment = soup.find_all('p' , {'class' : "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn"})
            note = soup.find_all('div', {"class" : "styles_reviewHeader__iU9Px"})
            pays = soup.find_all('div', {"class" : "typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua"})
            date_time = soup.find_all('time', {'class' : ""})
            
            for nb_avis in range(len(comment)):
                liste_note.append(note[nb_avis]['data-service-review-rating'])
                liste_date.append(date_time[nb_avis]['datetime'][0:19].replace('T', ' '))
                liste_pays.append(pays[nb_avis].span.text)
                
                try :
                    liste_commentaire.append(comment[nb_avis].text)
                
                except:
                    liste_commentaire.append('NaN')

            sleep(5)

        # constitution d'un dictionnaire regroupant les données
        dico = {'note' : liste_note, 'commentaire' : liste_commentaire, 'pays' : liste_pays, 'date' : liste_date}

        # constitution d'un DataFrame à partir du dictionnaire 
        df = pd.DataFrame(dico)

        # affichage du temps de calcul par rapport  à l'initialisation en début de requête 
        print('le temps de calcul est de {:.2f} secondes'.format(time()-t0))
        # print("Longueur du df : ", len(df))
        return (df)

