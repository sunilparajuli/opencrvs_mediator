from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from webhook_handler.utils.crvs_to_imis_converter import map_fhir_to_openimis
import requests
import logging
from webhook_handler.utils.crvs_auth_token import get_opencrvs_auth_token
from webhook_handler.utils.configurations import get_configuration
from .models import *
from django.shortcuts import render
import json

logger = logging.getLogger(__name__)



def webhook_manager(request):
    return render(request, 'index.html')


class SubscriptionView(APIView):
    def post(self, request):
        data = request.data
        print("request data", request.data)
        topic = data.get("topic")
        if not topic:
            return Response(
                {"message": "Topic required BIRTH_REGISTERED or DEATH_REGISTERED"},
                status=status.HTTP_400_BAD_REQUEST,
            )              
        config = get_configuration()
        if not config["webhook_url"]:
            return Response({"error": "Webhook URL not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        callback_url = data.get('callback_url', config["webhook_url"])
        existing_subscription = Subscription.objects.filter(topic=topic, callback_url=callback_url).first()        

        if existing_subscription:
            logger.info(f"Already subscribed to topic  {topic} with callback '{callback_url}'.")
            return Response(
                {"message": "Already subscribed.", "details": f"Topic: {topic}, Callback: {callback_url}"},
                status=status.HTTP_400_BAD_REQUEST,
            )        
        try:
            auth_token = get_opencrvs_auth_token(config["client_id"], config["client_secret"], config['auth_url'])
            response = requests.post(
                # config["webhook_url"],
                "http://localhost:5001/subscribe-webhook",
                json={
                    'hub': {
                        'callback': "http://localhost:5001/post-openimis",#callback_url,
                        'mode': 'subscribe',
                        'secret': config["sha_secret"],
                        'topic': f"{data.get('topic')}"
                    }
                },
                headers={
                    'Authorization': f'Bearer {auth_token}',
                    'Content-Type': 'application/json'
                }
            )
            if response.status_code in [200,202]:
                Subscription.objects.create(topic=topic, callback_url=callback_url)
                return Response({"response": True}, status=status.HTTP_202_ACCEPTED)
            else:
                logger.error(f"Subscription failed: {response.content}")
                return Response({"error": f"{response.json()}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error during subscription: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from webhook_handler.utils.get_imis_auth_token import get_bearer_token

def post_filtered_patient(filtered_patient, token):
    post_url = "https://imisbeta.hib.gov.np/api/api_fhir_r4/Patient/"
    
    # Headers including the Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Sending the filtered patient data to the Patient endpoint
    response = requests.post(post_url, headers=headers, json=filtered_patient)
    
    if response.status_code == 201:
        logger.info("Successfully posted the patient data.")
    else:
        print(f"response data", response)
        logger.error(f"Failed to post patient data, status code: {response.status_code}, response: {response.text}")


# Function to update or transform JSON with added fields
def transform_patient_resources_with_practitioner(resources):
    transformed = []
    for resource in resources:
        transformed.append({
            "resourceType": "Patient",
            "id": resource["id"],
            "name": resource.get("name", []),
            "telecom": resource.get("telecom", []),
            "gender": resource.get("gender", ""),
            "birthDate": resource.get("birthDate", ""),
            "address": [
                {
                    "extension": [
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-municipality",
                            "valueString": "Tikapur Municipality"
                        },
                        {
                            "url": "https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-location-reference",
                            "valueReference": {
                                "reference": "Location/D8C2B724-6D33-4E87-8113-9D10884FACA9",
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
                                    "value": "D8C2B724-6D33-4E87-8113-9D10884FACA9"
                                }
                            }
                        }
                    ],
                    "use": "home",
                    "type": "physical",
                    "city": "9",
                    "district": "Kailali",
                    "state": "Sudurpashchim"
                }
            ],
            "generalPractitioner": [
                {
                    "reference": "Organization/B53A657B-9875-4112-8857-9C7A46FB91EA",
                    "type": "Organization",
                    "identifier": {
                        "type": {
                            "coding": [
                                {
                                    "system": "https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/openimis-identifiers",
                                    "code": "UUID"
                                }
                            ]
                        },
                        "value": "B53A657B-9875-4112-8857-9C7A46FB91EA"
                    }
                }
            ],
            "contact": [
                {
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "system": "CodeSystem/patient-contact-relationship",
                                    "code": "3",
                                    "display": "Relative"
                                }
                            ]
                        }
                    ],
                    "name": resource.get("name", [])[0] if resource.get("name") else None
                }
            ]
        })
    return transformed



class WebhookEventView(APIView):
    def post(self, request):
        # Log the incoming payload
        print(request.data)
        logger.info(f"Received webhook payload: {request.data}")
        entries = request.data.get("event", {}).get("context", [])[0].get("entry", [])

        filtered_patient_resources = [
            entry["resource"]
            for entry in entries
            if entry.get("resource", {}).get("resourceType") == "Patient"
            and any(
                coding.get("system") == "http://opencrvs.org/specs/identifier-type"
                and coding.get("code") == "BIRTH_REGISTRATION_NUMBER"
                for identifier in entry["resource"].get("identifier", [])
                for coding in identifier.get("type", {}).get("coding", [])
            )
        ]

        transformed_patient_resources = transform_patient_resources_with_practitioner(filtered_patient_resources)
        token = get_bearer_token()
        
        if  token:
            # Post the filtered patient data to the API
            post_filtered_patient(filtered_patient_resources[0], token)        
        return Response({"message": f"Event received and processed successfully"}, status=200)


class ListAppWebhooksAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Define the necessary configuration
            config = get_configuration()
            BASE_URL = "http://localhost:2525/webhooks"
            auth_token = get_opencrvs_auth_token(config["client_id"], config["client_secret"], config['auth_url'])

            # Set headers and payload
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
            payload = {
                "hub": {
                    "callback": "http://localhost:5001/post-openimis",#"http://localhost:8000/api/webhooks/",
                    "mode": "subscribe",
                    "topic": "BIRTH_REGISTERED",
                    "secret": "b15e2dab-6362-408b-b3b9-e8d76e77ac22"
                }
            }

            # Make the GET request to the webhook service
            response = requests.get(BASE_URL, headers=headers, json=payload)
            response.raise_for_status()

            # Return the entries in the response
            data = response.json()
            return Response(data, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)

class DeleteWebHooksAPIView(APIView):
    config = get_configuration()
    BASE_URL = "http://localhost:2525/webhooks"
    auth_token = get_opencrvs_auth_token(config["client_id"], config["client_secret"], config['auth_url'])    
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    HUB_PAYLOAD = {
        "hub": {
            "callback": "http://localhost:8000/api/webhooks/",
            "mode": "subscribe",
            "topic": "BIRTH_REGISTERED",
            "secret": "b15e2dab-6362-408b-b3b9-e8d76e77ac22"
        }
    }

    def get_webhook_entries(self):
        """
        Fetch all webhook entries.
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.HEADERS)
            if response.status_code == 200:
                data = response.json()
                Subscription.objects.all().delete()
                return data.get("entries", [])
            else:
                logger.error(f"Failed to fetch entries: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching webhook entries: {str(e)}")
            return []

    def delete_webhook_entry(self, entry_id):
        """
        Delete a specific webhook entry by ID.
        """
        url = f"{self.BASE_URL}/{entry_id}"
        try:
            response = requests.delete(url, headers=self.HEADERS, json=self.HUB_PAYLOAD)
            if response.status_code == 204:
                logger.info(f"Successfully deleted webhook entry with id: {entry_id}")
                return True
            else:
                logger.error(f"Failed to delete entry {entry_id}: {response.status_code}, {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error deleting webhook entry {entry_id}: {str(e)}")
            return False

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to delete all existing webhook entries.
        """
        entries = self.get_webhook_entries()
        if not entries:
            logger.info("No webhook entries to delete.")
            return Response(
                {"message": "No webhook entries to delete."},
                status=status.HTTP_200_OK
            )

        failed_deletions = []
        for entry in entries:
            success = self.delete_webhook_entry(entry["id"])
            if not success:
                failed_deletions.append(entry["id"])

        if failed_deletions:
            logger.error(f"Failed to delete some entries: {failed_deletions}")
            return Response(
                {"message": "Failed to delete some entries.", "failed_entries": failed_deletions},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info("All webhook entries deleted successfully.")
        return Response(
            {"message": "All webhook entries deleted successfully."},
            status=status.HTTP_200_OK
        )