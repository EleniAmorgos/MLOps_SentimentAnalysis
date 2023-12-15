import requests

# Requête GET sur le point de terminaison
response = requests.get('http://127.0.0.1:8001/')
print(response.text)

# ADMINISTRATION DES JEUX DE DONNEES

# Scrapping de trustpilot / cdiscount 30 derniers jours sur 50 pages
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YWRtaW46VEZIX2RzdE1MT1BTMjM='
}
payload = {
    'url': 'https://fr.trustpilot.com/review/www.cdiscount.com?date=last30days',
    'nbr_pages': 15
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

