import requests
import json
# Function to get the bearer token
def get_bearer_token():
    login_url = "https://imisbeta.hib.gov.np/api/api_fhir_r4/login/"
    login_data = {
        "username": "Admin",
        "password": "jFK8,@`8b{72"
    }
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            return token
        else:
            logger.error("Token not found in the response")
            return None
    else:
        logger.error(f"Failed to login, status code: {response.status_code}")
        return None