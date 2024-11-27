# utils.py

def map_fhir_to_openimis(request_data):
    """Utility function to map FHIR data to OpenIMIS format"""
    event_data = request_data.get('event')
    context = event_data.get('context') if event_data else None

    if not context:
        return None, "Invalid payload: Missing context"

    # Initialize a list to hold the mapped data
    mapped_data = []

    for entry in context[0]['entry']:
        resource = entry.get('resource')
        if resource:
            if resource.get('resourceType') == 'Patient':
                patient_data = map_patient_to_openimis(resource)
                mapped_data.append({'patient': patient_data})
            elif resource.get('resourceType') == 'RelatedPerson':
                related_person_data = map_related_person_to_openimis(resource)
                mapped_data.append({'related_person': related_person_data})
            elif resource.get('resourceType') == 'DocumentReference':
                document_data = map_document_reference_to_openimis(resource)
                mapped_data.append({'document_reference': document_data})
            elif resource.get('resourceType') == 'Task':
                task_data = map_task_to_openimis(resource)
                mapped_data.append({'task': task_data})

    return mapped_data, None


def map_patient_to_openimis(resource):
    """Map FHIR Patient data to OpenIMIS format"""
    patient_data = {
        'name': resource.get('name', [{}])[0].get('given', ''),
        'family_name': resource.get('name', [{}])[0].get('family', ''),
        'birth_date': resource.get('birthDate'),
        'gender': resource.get('gender'),
        'identifier': map_patient_identifiers(resource.get('identifier', [])),
        'address': map_address(resource.get('address', [])),
    }
    return patient_data


def map_related_person_to_openimis(resource):
    """Map FHIR RelatedPerson data to OpenIMIS format"""
    related_person_data = {
        'relationship': resource.get('relationship', {}).get('coding', [{}])[0].get('code'),
        'patient_reference': resource.get('patient', {}).get('reference'),
        'meta': resource.get('meta', {}),
    }
    return related_person_data


def map_document_reference_to_openimis(resource):
    """Map FHIR DocumentReference data to OpenIMIS format"""
    document_data = {
        'document_type': resource.get('type', {}).get('coding', [{}])[0].get('code'),
        'attachment': resource.get('content', [{}])[0].get('attachment', {}).get('data'),
        'status': resource.get('status'),
        'subject': resource.get('subject', {}).get('display'),
    }
    return document_data


def map_task_to_openimis(resource):
    """Map FHIR Task data to OpenIMIS format"""
    task_data = {
        'status': resource.get('status'),
        'intent': resource.get('intent'),
        'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
        'focus': resource.get('focus', {}).get('reference'),
        'identifier': map_task_identifiers(resource.get('identifier', [])),
    }
    return task_data


def map_address(address_data):
    """Map FHIR Address data to OpenIMIS format"""
    if address_data:
        return {
            'line': address_data[0].get('line', []),
            'district': address_data[0].get('district'),
            'state': address_data[0].get('state'),
            'country': address_data[0].get('country'),
        }
    return {}


def map_patient_identifiers(identifiers):
    """Map FHIR Patient identifiers to OpenIMIS format"""
    mapped_identifiers = []
    for identifier in identifiers:
        mapped_identifiers.append({
            'system': identifier.get('system'),
            'value': identifier.get('value'),
            'type': identifier.get('type', {}).get('coding', [{}])[0].get('code')
        })
    return mapped_identifiers


def map_task_identifiers(identifiers):
    """Map FHIR Task identifiers to OpenIMIS format"""
    mapped_identifiers = []
    for identifier in identifiers:
        mapped_identifiers.append({
            'system': identifier.get('system'),
            'value': identifier.get('value')
        })
    return mapped_identifiers
