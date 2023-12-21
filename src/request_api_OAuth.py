import requests


def get_access_token(username_to_test, password_to_test):
    token_url = "http://127.0.0.1:8001/token"   

    data = {
        "username": username_to_test,
        "password": password_to_test,
    }

    response = requests.post(token_url, data=data)

    # Si OK => Token
    if response.status_code == 200:
        # Parse the JSON response and extract the access token
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token
    else:
        # Gestion erreur
        print(f"Error: {response.status_code}, {response.text}")
        return None


# 3 types d'utilisateurs à tester :
credentials_to_test = [
    {"username": "toto", "password": "titi", "role_to_test" : "username inexistant"},  
    {"username": "alice", "password": "wrongPwd", "role_to_test" : "username existant, mauvais pwd"},  
    {"username": "alice", "password": "wonderland", "role_to_test" : "user only"},  
    {"username": "admin", "password": "TFH_dstMLOPS23", "role_to_test" : "user + admin"} 
]

for credentials in credentials_to_test:
    username_to_test = credentials["username"]
    password_to_test = credentials["password"]
    print ("\n" , credentials["role_to_test"], ":")
    access_token = get_access_token(username_to_test,password_to_test)

    if access_token:
        # print(f"Access Token: {access_token}")
        # Header avec token
        headers = {'Authorization': f'Bearer {access_token}'}
        # Test du Endpoint sécurisé
        response = requests.get('http://127.0.0.1:8001/secured', headers=headers)
        print(response.text)

        # Scrapping de trustpilot  sur une liste d'enseignes 30 derniers jours sur N pages
        payload = {
            'liste_sites': ['ubaldi.com', 'habitatetjardin.com', 'menzzo.fr', 'fnac.com', 'darty.com', 'temu.com', 'cdiscount.com'],
            'nbr_pages': 1
        }
        response = requests.post('http://127.0.0.1:8001/scrap_last30days', headers=headers, json=payload)
        print(response.text)  

        # Transformation des données
        response = requests.post('http://127.0.0.1:8001/process_comments', headers=headers)
        print(response.text)  

        # Historisation des données
        response = requests.post('http://127.0.0.1:8001/histo_process_comments', headers=headers)
        print(response.text)
    else:
        print("Echec de l'obtention du token")