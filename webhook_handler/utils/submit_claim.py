import requests
from datetime import datetime
from django.conf import settings
import logging
import random
import string
import json
from datetime import datetime
import os
from .claim_items import *
logger = logging.getLogger(__name__)



def generate_claim_code():
    # Generate a random 5-digit number
    random_digits = ''.join(random.choices(string.digits, k=5))
    
    # Combine with 'CID' to form the claim code
    claim_code = f"NEP{random_digits}"
    
    return claim_code


def load_claim_items():
    """Loads claim items from `claim_items.py`."""
    try:
        items = claim_items_data.get("items", [])

        # Calculate total price dynamically
        total_amount = sum(item["unitPrice"]["value"] * item["quantity"]["value"] for item in items)

        return items, total_amount
    except Exception as e:
        logger.error(f"Error loading claim items: {e}")
        return [], 0.0
    

def submit_fhir_claim_to_openimis(patient_uuid, token, claim_data=None):
    """
    Submits a FHIR-compliant claim to OpenIMIS for the given patient UUID.

    :param patient_uuid: The UUID of the patient (e.g., "Patient/<uuid>").
    :param token: Authorization token for API requests.
    :param claim_data: Optional claim data to include in the payload.
    :return: Response from the OpenIMIS API if successful, None otherwise.
    """
    try:
        claim_items, total_value = load_claim_items()
        claim_payload = {
            "resourceType": "Claim",
            "billablePeriod": {
                "end": datetime.now().strftime("%Y-%m-%d"),
                "start": datetime.now().strftime("%Y-%m-%d"),
            },
            "created": datetime.now().strftime("%Y-%m-%d"), 
            "diagnosis": [
                {
                    "diagnosisReference": {"reference": "Condition/A02"},
                    "sequence": 1,
                    "type": [{"coding": [{"code": "icd_0"}]}],
                }
            ],
            "enterer": {
                "reference": f"Practitioner/{settings.PRACTITIONER}"
            },
            "facility": {
                "reference": f"Location/{settings.LOCATION}"
            },
            "id": "858A706A-A6BF-48DC-998D-30EFDAF8EDD2",
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "code": "UUID",
                                "system": "https://hl7.org/fhir/valueset-identifier-type.html",
                            }
                        ]
                    },
                    "use": "usual",
                    "value": "858A706A-A6BF-48DC-998D-30EFDAF8EDD2",  
                },
                {
                    "type": {
                        "coding": [
                            {
                                "code": "MR",
                                "system": "https://hl7.org/fhir/valueset-identifier-type.html",
                            }
                        ]
                    },
                    "use": "usual",
                    "value": f"{generate_claim_code()}",  
                },
            ],
            "insurance": [
                {
                    "coverage": {
                        "reference": f"Coverage/{settings.COVERAGE}"  
                    },
                    "focal": True,
                    "sequence": 1,
                }
            ],
            "item": claim_items,  # Populate with claim_data if provided
            "patient": {"reference": f"Patient/{patient_uuid}"},
            "priority": {"coding": [{"code": "normal"}]},
            "provider": {
                "reference": f"PractitionerRole/{settings.PRACTITIONERROLE}"  
            },
            "status": "active",
            "total": {
                "currency": "$",
                "value": total_value,  
            },
            "type": {"text": "O"},  
            "use": "claim",
            "supportingInfo": [
                {
                    "sequence": 1,
                    "category": {
                        "coding": [
                            {
                                "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/claim-supporting-info-category",
                                "code": "guarantee",
                            }
                        ]
                    },
                    "valueString": "121212",
                }
            ],
        }

        # Merge additional claim data if provided 
        if claim_data:
            claim_payload["item"] = claim_data.get("item", [])
            claim_payload["total"]["value"] = claim_data.get("total", 1.0)

        # Submit the claim to OpenIMIS
        # claim_url = f"{settings.OPENIMIS_FHIR_CLAIM_URL}"  # Replace with the actual OpenIMIS FHIR endpoint
        claim_url = settings.OPENHIM_URL + "/post-claim"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(claim_url, headers=headers, json=claim_payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        logger.info(f"FHIR Claim submitted successfully for patient {patient_uuid}.")
        return response.json()  # Return the response data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error submitting FHIR Claim to OpenIMIS: {str(e)}")
        return None
