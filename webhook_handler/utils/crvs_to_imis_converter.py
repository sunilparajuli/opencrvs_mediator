import json
import uuid  # Add this line
import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response


def extract_identifier_value(resource):
    """
    Extract the first value from the identifier list.
    """
    identifiers = resource.get("identifier", [])
    return identifiers[0]["value"] if identifiers else "11112223"

# Function to map patient data
def map_patient_data(resource, is_head=False, group_reference_id=None):
    """
    Maps a Patient resource to the required structure.
    :param resource: The source FHIR Patient resource.
    :param is_head: Boolean to indicate if this Patient is the head of the family.
    :param group_reference_id: JSON structure for the group reference to use for family members.
    """
    import uuid

    patient_id = str(uuid.uuid4())  # Generate unique ID for the patient
    identifier_value = extract_identifier_value(resource)  # Extract the value from 'identifier'

    extensions = [
        {
            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/patient-is-head",
            "valueBoolean": is_head
        },
        {
            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/patient-card-issued",
            "valueBoolean": False
        }
    ]

   # Add group reference for non-head patients
    if not is_head and group_reference_id:
        extensions.append(
            {
                "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/patient-group-reference",
                "valueReference": {
                    "reference": f"Group/{group_reference_id}",
                    "type": "Group",
                    "identifier": {
                        "type": {
                            "coding": [
                                {
                                    "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                    "code": "UUID"
                                }
                            ]
                        },
                        "value": group_reference_id
                    }
                }
            }
        )

    mapped_patient = {
        "resourceType": "Patient",
        "id": patient_id,
        "extension": extensions,
        "identifier": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                            "code": "UUID"
                        }
                    ]
                },
                "value": patient_id
            },
            {
                "type": {
                    "coding": [
                        {
                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                            "code": "Code"
                        }
                    ]
                },
                "value": identifier_value  # Use the extracted identifier value
            }
        ],
        "name": [
            {
                "use": "usual",
                "family": resource["name"][0]["family"][0],
                "given": [resource["name"][0]["given"][0]]
            }
        ],
        "gender": resource.get("gender", "male"),  # Default gender is "male"
        "birthDate": resource["birthDate"],
        "address": [
            {
                "extension": [
                    {
                        "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-municipality",
                        "valueString": "Achi"
                    },
                    {
                        "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-location-reference",
                        "valueReference": {
                            "reference": "Location/8ed4eb0d-61ae-4022-8b4c-3076a619f957",
                            "type": "Location",
                            "identifier": {
                                "type": {
                                    "coding": [
                                        {
                                            "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                            "code": "UUID"
                                        }
                                    ]
                                },
                                "value": "8ed4eb0d-61ae-4022-8b4c-3076a619f957"
                            }
                        }
                    }
                ],
                "use": "home",
                "type": "physical",
                "text": "Jetset zone 85",
                "city": "Rachla",
                "district": "Rapta",
                "state": "Ultha"
            }
        ]
    }

    import json
    print(json.dumps(mapped_patient, indent=2))

    # import pdb;pdb.set_trace()

    return mapped_patient
