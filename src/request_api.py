import requests

# Requête GET sur le point de terminaison
response = requests.get('http://127.0.0.1:8001/')
print(response.text)

# ADMINISTRATION DES JEUX DE DONNEES

# Scrapping de trustpilot  sur une liste d'enseignes 30 derniers jours sur N pages
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YWRtaW46VEZIX2RzdE1MT1BTMjM='
}
payload = {
    'liste_sites': ['ubaldi.com', 'habitatetjardin.com', 'menzzo.fr', 'fnac.com', 'darty.com', 'temu.com', 'cdiscount.com'],
    'nbr_pages': 3
}
response = requests.post('http://127.0.0.1:8001/scrap_last30days', headers=headers, json=payload)
print(response.text)


# Transformation des données
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YWRtaW46VEZIX2RzdE1MT1BTMjM='
}

response = requests.post('http://127.0.0.1:8001/process_comments', headers=headers)
print(response.text)



# Historisation des données
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YWRtaW46VEZIX2RzdE1MT1BTMjM='
}

response = requests.post('http://127.0.0.1:8001/histo_process_comments', headers=headers)
print(response.text)

