import requests
import logging
import os  # Recommended for environment variables

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get the bearer token
def get_bearer_token():
    login_url = "https://imisbeta.hib.gov.np/api/api_fhir_r4/login/"
    
    # Fetch credentials from environment variables
    username = os.getenv("IMIS_USERNAME", "Admin")  # Default to "Admin" if not set
    password = os.getenv("IMIS_PASSWORD", "jFK8,@`8b{72")  # Default to hardcoded password if not set
    
    login_data = {
        "username": username,
        "password": password,
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        
        token = response.json().get("token")
        if token:
            logger.info("Successfully retrieved bearer token.")
            return token
        else:
            logger.error("Token not found in the response.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to login: {e}")
        return None
