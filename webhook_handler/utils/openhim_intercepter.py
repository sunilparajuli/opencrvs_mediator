import requests
import logging
# from .auth_token import get_opencrvs_auth_token
from requests.auth import HTTPBasicAuth
from django.conf import settings
# Constants
import base64


# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def put_data_to_openhim_mediator(auth_token, data):
    """Send data to OpenHIM Mediator with provided auth token."""
    try:
        response = requests.post(
            settings.OPENHIM_URL,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {auth_token}'
            }
        )
        if response.status_code != 200:
            logger.error(f"Failed response from OpenHIM Mediator: {response.status_code} - {response.text}")
            return None
        return response
    except requests.RequestException as error:
        logger.error(f"Request failed: {error}")
        return None

# def put_data_to_openhim_mediator_with_token(data):
#     """Get auth token and send data to OpenHIM Mediator."""
#     auth_token = get_opencrvs_auth_token()
#     if not auth_token:
#         logger.error("Cannot create token")
#         return None
#     return put_data_to_openhim_mediator(auth_token, data)


def send_fhir_request_openhim_server(endpoint_path, data=None, method="GET"):
    """
    Send a request to the OpenHIM FHIR endpoint with a specific path and method,
    using Base64-encoded authentication.
    """
    # Ensure `OPENHIM_MEDIATOR_URL` is defined and ends with a `/`
    OPENHIM_MEDIATOR_URL = "http://localhost:5001"  # Replace with your actual URL
    full_url = OPENHIM_MEDIATOR_URL + endpoint_path
    print("URL:", full_url)

    # Encode username and password in Base64
    username = "test"
    password = "test"
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Define headers with Base64 Authorization
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }
    try:
        # Use the appropriate HTTP method
        response = requests.request(method, full_url, json=data, headers=headers)
        return response
    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        return None