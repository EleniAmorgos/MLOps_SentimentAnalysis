import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from time import time
import datetime


class WebScrapping_RatedComments():
    @staticmethod
    def WebScrapping_Comments(liste_sites, nbr_pages):
        print (liste_sites)
        liste_url = []
        # constitution des listes qui serviront à consolider les donnees
        liste_note = []
        liste_commentaire = []
        liste_date = []
        liste_site = []

        # initialisation de l'heure maintenant 
        t0 = time()
        # scapping des données
        for site in liste_sites : 
            print(site)
            page = 1
            while page <= nbr_pages :
                try :
                    if requests.get('https://fr.trustpilot.com/review/www.' + site + '?date=last30days&page=' + str(page)).status_code==200:
                        liste_url.append('https://fr.trustpilot.com/review/www.' + site + '?date=last30days&page='+str(page))
                except:
                    pass
                page = page + 1
            
            print(len(liste_url), "valid pages to scrap")

        for url in liste_url:
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            comment = soup.find_all('p' , {'class' : "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn"})
            note = soup.find_all('div', {"class" : "styles_reviewHeader__iU9Px"})
            date_time = soup.find_all('time', {'class' : ""})

            for nb_avis in range(len(comment)):
                liste_note.append(note[nb_avis]['data-service-review-rating'])
                liste_date.append(date_time[nb_avis]['datetime'][0:19].replace('T', ' '))
                liste_site.append(site)

                try :
                    liste_commentaire.append(comment[nb_avis].text)

                except:
                    liste_commentaire.append('NaN')

            sleep(5)
        
        print(" scrap fini")
        # constitution d'un dictionnaire regroupant les données
        dico = {'note' : liste_note, 'commentaire' : liste_commentaire, 'date' : liste_date, 'site' : liste_site}

        # constitution d'un DataFrame à partir du dictionnaire 
        df = pd.DataFrame(dico)
        # Get the current date and time
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        df['scrap_date'] = formatted_datetime

        # affichage du temps de calcul par rapport  à l'initialisation en début de requête 
        print('le temps de calcul est de {:.2f} secondes'.format(time()-t0))
        # print("Longueur du df : ", len(df))
        return (df)

