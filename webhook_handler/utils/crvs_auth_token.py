import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

# Suppress the InsecureRequestWarning, DONT DO THIS IN PRODUCTION
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

def get_opencrvs_auth_token(client_id, client_secret, auth_url):
    #auth_url = config.get("auth_url", "http://localhost:4040/token")

    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    try:
        response = requests.post(
            auth_url,
            params=params,
            headers={'Content-Type': 'application/json'},
            verify=False  # Disable SSL verification (not recommended for production)
        )
        if response.status_code in [200,202]:
            data = response.json()
            access_token = data.get('access_token')
            logger.info("Successfully retrieved access token.")
            return access_token
        else:
            logger.error(f"Failed to retrieve token. Status Code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error while fetching auth token: {str(e)}")
        return None
