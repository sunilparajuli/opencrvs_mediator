import requests
from datetime import datetime
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


def submit_fhir_claim_to_openimis(patient_uuid, token, claim_data=None):
    """
    Submits a FHIR-compliant claim to OpenIMIS for the given patient UUID.
    
    :param patient_uuid: The UUID of the patient (e.g., "Patient/<uuid>").
    :param token: Authorization token for API requests.
    :param claim_data: Optional claim data to include in the payload.
    :return: Response from the OpenIMIS API if successful, None otherwise.
    """
    try:
        claim_payload = {
            "resourceType": "Claim",
            "billablePeriod": {
                "end": "2018-10-03",  
                "start": "2018-10-03"  
            },
            "created": "2018-10-03",  # Replace with dynamic date if needed
            "diagnosis": [
                {
                    "diagnosisReference": {
                        "reference": "Condition/A02"  
                    },
                    "sequence": 1,
                    "type": [
                        {
                            "coding": [
                                {
                                    "code": "icd_0"  
                                }
                            ]
                        }
                    ]
                }
            ],
            "enterer": {
                "reference": "Practitioner/6F480233-5A7B-4034-8107-17B419E32498"  
            },
            "facility": {
                "reference": "HealthcareService/D61C869B-F184-4CAE-B61B-0AD52DDE2354"  
            },
            "id": "858A706A-A6BF-48DC-998D-30EFDAF8EDD2",  
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "code": "UUID",
                                "system": "https://hl7.org/fhir/valueset-identifier-type.html"
                            }
                        ]
                    },
                    "use": "usual",
                    "value": "858A706A-A6BF-48DC-998D-30EFDAF8EDD2"  # Replace with dynamic value if needed
                },
                {
                    "type": {
                        "coding": [
                            {
                                "code": "MR",
                                "system": "https://hl7.org/fhir/valueset-identifier-type.html"
                            }
                        ]
                    },
                    "use": "usual",
                    "value": "CID00001"  # Replace with dynamic value if needed
                }
            ],
            "insurance": [
                {
                    "coverage": {
                        "reference": "Coverage/28D8DF61-890E-4B1C-A66F-BE02208C99D4"  # Replace with dynamic reference if needed
                    },
                    "focal": True,
                    "sequence": 0
                }
            ],
            "item": [],  # Populate with claim_data if provided
            "patient": {
                "reference": f"Patient/{patient_uuid}"
            },
            "priority": {
                "coding": [
                    {
                        "code": "normal"
                    }
                ]
            },
            "provider": {
                "reference": "PractitionerRole/6F480233-5A7B-4034-8107-17B419E32498"  # Replace with dynamic reference if needed
            },
            "status": "active",
            "total": {
                "currency": "$",
                "value": 0.0  # Populate with claim_data if provided
            },
            "type": {
                "text": "O"  # Replace with dynamic value if needed
            },
            "use": "claim",
            "supportingInfo": [
                {
                    "category": {
                        "coding": [
                            {
                                "code": "attachment",
                                "display": "Attachment"
                            }
                        ],
                        "text": "attachment"
                    },
                    "valueAttachment": {
                        "contentType": "image/png",
                        "creation": "2020-12-01",
                        "data": "[BASE64_ENCODED_STRING]",  # Replace with actual base64 string
                        "hash": "7d14f68a8489094737aa52e1db27042df708f691",
                        "title": "openimis-logo.png"
                    }
                }
            ]
        }
        
        # Merge additional claim data if provided
        if claim_data:
            claim_payload["item"] = claim_data.get("item", [])
            claim_payload["total"]["value"] = claim_data.get("total", 0.0)
        
        # Submit the claim to OpenIMIS
        claim_url = f"{settings.OPENIMIS_FHIR_CLAIM_URL}"  # Replace with the actual OpenIMIS FHIR endpoint
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