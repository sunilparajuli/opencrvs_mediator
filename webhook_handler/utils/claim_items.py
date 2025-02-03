# openimis-mediator/claim_items.py

claim_items_data = {
    "items": [
        {
            "extension": [
                {
                    "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/claim-item-reference",
                    "valueReference": {
                        "reference": "ActivityDefinition/488d8bcb-5b88-438c-9077-f177f6f32626",
                        "type": "ActivityDefinition",
                        "identifier": {
                            "type": {
                                "coding": [
                                    {
                                        "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                        "code": "UUID"
                                    }
                                ]
                            },
                            "value": "488d8bcb-5b88-438c-9077-f177f6f32626"
                        }
                    }
                }
            ],
            "sequence": 1,
            "category": {
                "text": "service"
            },
            "productOrService": {
                "text": "A1"
            },
            "quantity": {
                "value": 1.0
            },
            "unitPrice": {
                "value": 400.0,
                "currency": "$"
            }
        },
       
    ]
}
