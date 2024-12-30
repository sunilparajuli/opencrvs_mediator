import uuid
import requests

def post_family_group(processed_ids, token):
    """
    Creates and posts a Group resource based on processed Patient IDs.

    Args:
        processed_ids (dict): Dictionary containing `child`, `mother`, and `father` patient IDs.
        token (str): Bearer token for authorization.

    Raises:
        Exception: If posting the Group fails.
    """
    new_group_uuid = str(uuid.uuid4())  # Generate a new UUID for the Group
    import pdb;pdb.set_trace()
    group_payload = {
        "resourceType": "Group",
        "id": new_group_uuid,
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
                "value": new_group_uuid
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
                "value": "GROUP12345"
            }
        ],
        "active": True,
        "type": "Person",
        "actual": True,
        "name": "Example Group Name",
        "quantity": len(processed_ids),
        "extension": [
            {
                "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/group-address",
                "valueAddress": {
                    "extension": [
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-municipality",
                            "valueString": "Example Municipality"
                        },
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-location-reference",
                            "valueReference": {
                                "reference": "Location/new-location-uuid",
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
                                    "value": "new-location-uuid"
                                }
                            }
                        }
                    ],
                    "use": "home",
                    "type": "physical",
                    "text": "123 Example Street",
                    "city": "Example City",
                    "district": "Example District",
                    "state": "Example State"
                }
            }
        ],
        "member": []
    }

    # Add members dynamically from processed IDs
    for role, uuid in processed_ids.items():
        if uuid:
            group_payload["member"].append({
                "entity": {
                    "reference": f"Patient/{uuid}",
                    "type": "Patient",
                    "identifier": {
                        "type": {
                            "coding": [
                                {
                                    "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                    "code": "UUID"
                                }
                            ]
                        },
                        "value": uuid
                    },
                    "display": role.capitalize()  # Display role as a label (Child, Mother, Father)
                }
            })

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post("https://demoimis.tinker.com.np/api/api_fhir_r4/Group/", json=group_payload, headers=headers)

    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to post Group: {response.status_code}, {response.text}")

    return response.json()
