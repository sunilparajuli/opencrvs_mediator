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



class WebhookEventView(APIView):
    """
    Handles incoming webhook events and processes Patient and Person resources.
    """
    def post(self, request):
        logger.info("Received webhook event.")
        
        entries = request.data.get("event", {}).get("context", [])[0].get("entry", [])

        if not entries:
            logger.error("No entries found in webhook payload.")
            return Response({"message": "No entries found."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract Patient and RelatedPerson resources
        patient_resources = [
            entry["resource"] for entry in entries if entry.get("resource", {}).get("resourceType") == "Patient"
        ]
        related_person_resources = [
            entry["resource"] for entry in entries if entry.get("resource", {}).get("resourceType") == "RelatedPerson"
        ]

        if not patient_resources:
            logger.error("No Patient resources found in the payload.")
            return Response({"message": "No Patient resources found."}, status=status.HTTP_400_BAD_REQUEST)

        # Get authorization token
        token = get_bearer_token()
        if not token:
            logger.error("Failed to retrieve authorization token.")
            return Response({"message": "Authorization token retrieval failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Initialize placeholders for child, mother, and father
        child = None
        father = None
        mother = None

        # Identify CHILD using BIRTH_REGISTRATION_NUMBER
        for patient_resource in patient_resources:
            if any(
                identifier.get("type", {}).get("coding", [])[0].get("code") == "BIRTH_REGISTRATION_NUMBER"
                for identifier in patient_resource.get("identifier", [])
            ):
                child = patient_resource
                logger.info("Identified CHILD patient.")
                break

        # Remove CHILD from the list to avoid misclassification
        if child:
            patient_resources.remove(child)

        # Map RelatedPerson to identify MOTHER
        for related_person in related_person_resources:
            relationship = related_person.get("relationship", {}).get("coding", [])[0].get("code")
            patient_ref = related_person.get("patient", {}).get("reference")
            matched_patient = next((p for p in patient_resources if f"Patient/{p.get('id')}" == patient_ref), None)
            if relationship == "MOTHER" and matched_patient:
                mother = matched_patient
                logger.info("Identified MOTHER patient.")
                patient_resources.remove(mother)
                break

        # The remaining patient resource is FATHER
        if patient_resources:
            father = patient_resources[0]
            logger.info("Identified FATHER patient.")

        # Process CHILD
        import pdb;pdb.set_trace()
        if child:
            try:
                mapped_child = map_patient_data(child, is_head=False)
                logger.info(f"Mapped CHILD Data: {json.dumps(mapped_child)}")
                post_filtered_patient(mapped_child, token)
            except Exception as e:
                logger.error(f"Error processing CHILD data: {str(e)}")

        # Process FATHER
        if father:
            try:
                mapped_father = map_patient_data(father, is_head=False)
                logger.info(f"Mapped FATHER Data: {json.dumps(mapped_father)}")
                post_filtered_patient(mapped_father, token)
            except Exception as e:
                logger.error(f"Error processing FATHER data: {str(e)}")

        # Process MOTHER
        if mother:
            try:
                mapped_mother = map_patient_data(mother, is_head=False)
                logger.info(f"Mapped MOTHER Data: {json.dumps(mapped_mother)}")
                post_filtered_patient(mapped_mother, token)
            except Exception as e:
                logger.error(f"Error processing MOTHER data: {str(e)}")

        return Response({"message": "Event received and processed successfully."}, status=status.HTTP_200_OK)
