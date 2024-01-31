
import requests
import pytest

url = 'http://127.0.0.1:8001'

def get_access_token(username_to_test, password_to_test):
    token_url = url+"/token"   

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

def test_get_access_token():
    # Test with correct credentials
    access_token = get_access_token("alice", "wonderland")
    assert access_token is not None

    # Test with incorrect credentials
    access_token = get_access_token("invalid_user", "invalid_password")
    assert access_token is None


def test_secured_endpoint():
    credentials_to_test = [
        {"username": "invalid_user", "password": "invalid_password" , "expected_status_code" : 401},  
        {"username": "alice", "password": "wrongPwd", "expected_status_code" : 401},  
        {"username": "alice", "password": "wonderland", "expected_status_code" : 200 },  
        {"username": "admin", "password": "adminADMIN", "expected_status_code" : 200} 
    ]

    for credentials in credentials_to_test:
        access_token = get_access_token(credentials["username"], credentials["password"])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(url + '/secured', headers=headers)
        assert response.status_code == credentials["expected_status_code"]


def test_add_user():
    payload_user_to_add = {"username": "new_user", "password": "new_password", "role": ["user"]}
 
    not_admin_credentials = {"username": "alice", "password": "wonderland"}
    not_admin_token = get_access_token(not_admin_credentials["username"], not_admin_credentials["password"])
    headers = {'Authorization': f'Bearer {not_admin_token}'}

    # Test adding a user (should fail)
    response = requests.post(url + '/add_user', headers=headers, json=payload_user_to_add)
    assert response.status_code == 403

    admin_credentials = {"username": "admin", "password": "adminADMIN"}
    admin_token = get_access_token(admin_credentials["username"], admin_credentials["password"])
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Test adding a user (success)
    response = requests.post(url + '/add_user', headers=headers, json=payload_user_to_add)
    assert response.status_code == 200

    # Test adding the same user again (should fail)
    response = requests.post(url + '/add_user', headers=headers, json=payload_user_to_add)
    assert response.status_code == 400




def test_delete_user():
    payload_user_to_delete = {"username": "new_user"}
 
    not_admin_credentials = {"username": "alice", "password": "wonderland"}
    not_admin_token = get_access_token(not_admin_credentials["username"], not_admin_credentials["password"])
    headers = {'Authorization': f'Bearer {not_admin_token}'}

    # Test deleting a user (should fail)
    response = requests.delete(url + '/delete_user', headers=headers, json=payload_user_to_delete)
    assert response.status_code == 403

    admin_credentials = {"username": "admin", "password": "adminADMIN"}
    admin_token = get_access_token(admin_credentials["username"], admin_credentials["password"])
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Test deleting a user (success)
    response = requests.delete(url + '/delete_user', headers=headers, json=payload_user_to_delete)
    assert response.status_code == 200

    # Test deleting the same user again (should fail)
    response = requests.delete(url + '/delete_user', headers=headers, json=payload_user_to_delete)
    assert response.status_code == 400

        
# ******************************************************************
# ****************    SCRAPPING  ***********************************
# ******************************************************************


def test_scrap_last30days():
    payload = {
            'liste_sites': ['ubaldi.com', 'habitatetjardin.com', 'menzzo.fr', 'fnac.com', 'darty.com', 'temu.com', 'cdiscount.com'],
            'nbr_pages': 1
        }
 
    not_admin_credentials = {"username": "alice", "password": "wonderland"}
    not_admin_token = get_access_token(not_admin_credentials["username"], not_admin_credentials["password"])
    headers = {'Authorization': f'Bearer {not_admin_token}'}

    # Test scrapping as user (should fail)
    response = requests.post(url+'/scrap_last30days', headers=headers, json=payload)
    assert response.status_code == 403

    admin_credentials = {"username": "admin", "password": "adminADMIN"}
    admin_token = get_access_token(admin_credentials["username"], admin_credentials["password"])
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Test scrapping as admin (success)
    response = requests.post(url+'/scrap_last30days', headers=headers, json=payload)
    assert response.status_code == 200
 


def test_process_comments():

    not_admin_credentials = {"username": "alice", "password": "wonderland"}
    not_admin_token = get_access_token(not_admin_credentials["username"], not_admin_credentials["password"])
    headers = {'Authorization': f'Bearer {not_admin_token}'}

    # Test scrapping as user (should fail)
    response = requests.post(url+'/process_comments', headers=headers)
    assert response.status_code == 403

    admin_credentials = {"username": "admin", "password": "adminADMIN"}
    admin_token = get_access_token(admin_credentials["username"], admin_credentials["password"])
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Test scrapping as admin (success)
    response = requests.post(url+'/process_comments', headers=headers)
    assert response.status_code == 200

# def test_histo_process_comments():

#     not_admin_credentials = {"username": "alice", "password": "wonderland"}
#     not_admin_token = get_access_token(not_admin_credentials["username"], not_admin_credentials["password"])
#     headers = {'Authorization': f'Bearer {not_admin_token}'}

#     # Test scrapping as user (should fail)
#     response = requests.post(url+'/histo_process_comments', headers=headers)
#     assert response.status_code == 403

#     admin_credentials = {"username": "admin", "password": "adminADMIN"}
#     admin_token = get_access_token(admin_credentials["username"], admin_credentials["password"])
#     headers = {'Authorization': f'Bearer {admin_token}'}

#     # Test scrapping as admin (success)
#     response = requests.post(url+'/histo_process_comments', headers=headers)
#     assert response.status_code == 200
