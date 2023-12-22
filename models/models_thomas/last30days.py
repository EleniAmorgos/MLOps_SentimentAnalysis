# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 19:01:12 2023

@author: t.fourtouill
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep

# definition du nombre de pages max à charger, liste des sites traites
nb_pages = 2
liste_sites = ['ubaldi.com', 'habitatetjardin.com', 'menzzo.fr', 'fnac.com', 'darty.com', 'temu.com', 'cdiscount.com']
liste_url = []

# constitution des listes qui serviront à consolider les donnees
liste_note = []
liste_commentaire = []
liste_date = []
liste_site = []

# scapping des données
for site in liste_sites : 
    page = 2
    while page <= nb_pages :
        try :
            if requests.get('https://fr.trustpilot.com/review/www.' + site + '?date=last30days&page=' + str(page)).status_code==200:
                liste_url.append('https://fr.trustpilot.com/review/www.' + site + '?date=last30days&page='+str(page))
        except:
            pass
        page = page + 1

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
    
# constitution d'un dictionnaire regroupant les données
dico = {'note' : liste_note, 'commentaire' : liste_commentaire, 'date' : liste_date, 'site' : liste_site}

# constitution d'un DataFrame à partir du dictionnaire 
df = pd.DataFrame(dico)

# update de de la base de donnée avec les valeur last30days 
base_comments = pd.read_csv('datasets/SatisfactionClients/trustpilot_comments.csv', sep=';')

date_comment_max = base_comments['date'].max()
df = df[df['date']>date_comment_max]

base_comments = base_comments.append(df, ignore_index=True)

# enregistrement des nouvelles données : historique + last30days chargees
base_comments.to_csv('datasets/SatisfactionClients/trustpilot_comments.csv', sep=';', index=False)

