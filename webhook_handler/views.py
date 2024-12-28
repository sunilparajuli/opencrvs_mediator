# Standard Library Imports
import json
import logging

# Third-Party Imports
import requests
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Imports
from webhook_handler.utils.crvs_auth_token import get_opencrvs_auth_token
from webhook_handler.utils.configurations import get_configuration
from webhook_handler.utils.crvs_to_imis_converter import map_patient_data
from webhook_handler.utils.get_imis_auth_token import get_bearer_token
from .models import *

# Logger Configuration
logger = logging.getLogger(__name__)


# View to handle webhook homepage (if applicable)
def webhook_manager(request):
    return render(request, 'index.html')


# Utility function to post filtered patient data
def post_filtered_patient(filtered_patient, token):
    """
    Posts filtered patient data to OpenIMIS FHIR API.
    """
    post_url = settings.OPENIMIS_FHIR_PATIENT_URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(post_url, headers=headers, json=filtered_patient)
        if response.status_code == 201:
            logger.info("Successfully posted the patient data.")
        else:
            logger.error(
                f"Failed to post patient data, status code: {response.status_code}, response: {response.text}"
            )
    except requests.RequestException as e:
        logger.error(f"Exception during patient data post: {str(e)}")


# API View to handle Webhook Events
class WebhookEventView(APIView):
    """
    Handles incoming webhook events and processes Patient resources.
    """
    def post(self, request):
        logger.info("Received webhook event.")

        print("request data", request.data)
        entries = request.data.get("event", {}).get("context", [])[0].get("entry", [])

        if not entries:
            logger.error("No entries found in webhook payload.")
            return Response({"message": "No Patient data found."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract Patient resources from entries
        patient_resources = [
            entry["resource"] for entry in entries if entry.get("resource", {}).get("resourceType") == "Patient"
        ]

        if not patient_resources:
            logger.error("No Patient resources found in the payload.")
            return Response({"message": "No Patient resources found."}, status=status.HTTP_400_BAD_REQUEST)

        # Get authorization token
        token = get_bearer_token()
        if not token:
            logger.error("Failed to retrieve authorization token.")
            return Response({"message": "Authorization token retrieval failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Process each Patient resource
        for idx, patient_resource in enumerate(patient_resources):
            try:
                is_head = idx == 0  # First patient is considered the head
                mapped_patient = map_patient_data(patient_resource, is_head=is_head)
                logger.info(f"Mapped Patient Data: {json.dumps(mapped_patient)}")
                post_filtered_patient(mapped_patient, token)
            except Exception as e:
                logger.error(f"Error processing patient data: {str(e)}")

        return Response({"message": "Event received and processed successfully."}, status=status.HTTP_200_OK)
