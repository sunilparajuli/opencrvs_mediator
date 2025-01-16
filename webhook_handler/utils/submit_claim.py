import requests
from datetime import datetime
from django.conf import settings

def submit_fhir_claim_to_openimis(patient_uuid, token, claim_data=None):
    """
    Submits a FHIR-compliant claim to OpenIMIS for the given patient UUID.
    
    :param patient_uuid: The UUID of the patient (e.g., "Patient/<uuid>").
    :param token: Authorization token for API requests.
    :param claim_data: Optional claim data to include in the payload.
    :return: Response from the OpenIMIS API if successful, None otherwise.
    """
    try:
        # Construct the FHIR Claim payload
        claim_payload = {
            "resourceType": "Claim",
            "status": "active",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                        "code": "professional"
                    }
                ]
            },
            "use": "claim",
            "patient": {
                "reference": f"Patient/{patient_uuid}"
            },
            "created": datetime.now().isoformat(),
            "insurer": {
                "reference": f"Organization/{settings.OPENIMIS_INSURER_ID}"
            },
            "provider": {
                "reference": f"Organization/{settings.OPENIMIS_PROVIDER_ID}"
            },
            "items": [],
            "total": {
                "value": 0.0,
                "currency": "USD"
            }
        }
        
        # Merge additional claim data if provided
        if claim_data:
            claim_payload["items"] = claim_data.get("items", [])
            claim_payload["total"]["value"] = claim_data.get("total", 0.0)
        
        # Submit the claim to OpenIMIS
        claim_url = f"{settings.OPENIMIS_BASE_URL}/api/api_fhir_r4/Claim/"  # Replace with the actual OpenIMIS FHIR endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/fhir+json",
        }
        
        response = requests.post(claim_url, headers=headers, json=claim_payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        logger.info(f"FHIR Claim submitted successfully for patient {patient_uuid}.")
        return response.json()  # Return the response data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error submitting FHIR Claim to OpenIMIS: {str(e)}")
        return None