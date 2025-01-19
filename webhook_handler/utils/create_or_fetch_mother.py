import logging
logger = logging.getLogger(__name__)
import requests
from django.conf import settings
import json
from webhook_handler.utils.crvs_to_imis_converter import map_patient_data
from webhook_handler.views import post_filtered_patient
def fetch_mother_from_openimis(identifier_value, token):
    """
    Fetches the mother's UUID from OpenIMIS using a unique identifier.
    
    :param identifier_value: The value of the unique identifier (e.g., BIRTH_REGISTRATION_NUMBER).
    :param token: Authorization token for API requests.
    :return: Mother's UUID if found, None otherwise.
    """
    try:
        # Replace with the actual OpenIMIS API endpoint for searching patients
        search_url = f"{settings.OPENIMIS_FHIR_PATIENT_URL}?identifier={identifier_value}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        patients = response.json().get("data", [])
        if patients:
            # Assuming the first match is the correct one
            return patients[0].get("id")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching MOTHER from OpenIMIS: {str(e)}")
    
    return None



def fetch_or_create_mother(mother_resource, token, group_reference_id=None):
    """
    Fetches the mother's UUID from OpenIMIS if she exists, otherwise creates a new entry.
    
    :param mother_resource: The mother's resource data.
    :param token: Authorization token for API requests.
    :param group_reference_id: Optional group reference ID for linking family members.
    :return: Mother's UUID if found or created, None otherwise.
    """
    # Extract a unique identifier for the mother (e.g., BIRTH_REGISTRATION_NUMBER)

    
    mother_identifier = next(
        (identifier["value"] for identifier in mother_resource.get("identifier", [])
        if identifier.get("value")),  # Check if "value" exists
        None
    )
    
    if not mother_identifier:
        logger.error("No unique identifier found for MOTHER.")
        return None
    
    # Fetch mother's information from OpenIMIS using the unique identifier
    mother_uuid = fetch_mother_from_openimis(mother_identifier, token)
    
    if mother_uuid:
        logger.info(f"MOTHER already exists in OpenIMIS with UUID: {mother_uuid}")
        return mother_uuid
    
    # If mother does not exist, create a new entry
    try:
        mapped_mother = map_patient_data(mother_resource, is_head=False, group_reference_id=group_reference_id)
        logger.info(f"Mapped MOTHER Data: {json.dumps(mapped_mother)}")
        response = post_filtered_patient(mapped_mother, token)
        
        if response and response.get("id"):
            logger.info(f"MOTHER created with UUID: {response['id']}")
            return response["id"]
    except Exception as e:
        logger.error(f"Error creating MOTHER in OpenIMIS: {str(e)}")
    
    return None