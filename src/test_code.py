import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from time import time

from data.web_scrapping import WebScrapping_RatedComments

# Url à scrapper 
url = 'https://fr.trustpilot.com/review/www.cdiscount.com?date=last30days'
# Nom du CSV où les données seront écrites
csv_filename = 'cdiscount_last30days.csv'
# Répertoire de données depuis le répertoire src
external_data_path = os.path.join('..', '..', 'data', 'external')
# print(external_data_path)
# Si le répertoire n'existe pas, on le crée
os.makedirs(external_data_path, exist_ok=True)
# Construit le chemin complet pour atteindre le csv
csv_filepath = os.path.join(external_data_path, csv_filename)
print(csv_filepath)


df = WebScrapping_RatedComments.WebScrapping_Comments(url_to_scrap=url, nbr_pages = 50)

print("Longueur du df : ", len(df))
print(df.head(10))
print(df.tail(10))

# Save the DataFrame to CSV
df.to_csv(csv_filepath, sep=';', quotechar='"', index=False)
print(f"Data written to: {csv_filepath}")