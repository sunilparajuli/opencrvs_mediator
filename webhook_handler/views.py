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
from webhook_handler.utils.group_reference import post_family_group
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
    Returns the patient ID if successful, None otherwise.
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
            patient_id = response.json().get('id')  # Capture the ID from the response
            logger.info(f"Patient ID: {patient_id}")
            return patient_id
        else:
            logger.error(
                f"Failed to post patient data, status code: {response.status_code}, response: {response.text}"
            )
            return None
    except requests.RequestException as e:
        logger.error(f"Exception during patient data post: {str(e)}")
        return None



class WebhookEventView1(APIView):
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
                # logger.info(f"Mapped FATHER Data: {json.dumps(mapped_father)}")
                post_filtered_patient(mapped_father, token)
            except Exception as e:
                logger.error(f"Error processing FATHER data: {str(e)}")

        # Process MOTHER
        if mother:
            try:
                mapped_mother = map_patient_data(mother, is_head=False)
                # logger.info(f"Mapped MOTHER Data: {json.dumps(mapped_mother)}")
                post_filtered_patient(mapped_mother, token)
            except Exception as e:
                logger.error(f"Error processing MOTHER data: {str(e)}")

        return Response({"message": "Event received and processed successfully."}, status=status.HTTP_200_OK)



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
        child_id = None
        father_id = None
        mother_id = None

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
        processed_ids = {}
        # Process CHILD
        if child:
            try:
                mapped_child = map_patient_data(child, is_head=False)
                logger.info(f"Mapped CHILD Data: {json.dumps(mapped_child)}")
                processed_ids["child"] = post_filtered_patient(mapped_child, token).get("id")
                import pdb;pdb.set_trace()
                logger.info(f"CHILD ID: {child_id}")
            except Exception as e:
                logger.error(f"Error processing CHILD data: {str(e)}")

        # Process FATHER
        if father:
            try:
                mapped_father = map_patient_data(father, is_head=False)
                logger.info(f"Mapped FATHER Data: {json.dumps(mapped_father)}")
                processed_ids["father"] = post_filtered_patient(mapped_father, token).get("id")
                logger.info(f"FATHER ID: {father_id}")
            except Exception as e:
                logger.error(f"Error processing FATHER data: {str(e)}")

        # Process MOTHER
        if mother:
            try:
                mapped_mother = map_patient_data(mother, is_head=False)
                logger.info(f"Mapped MOTHER Data: {json.dumps(mapped_mother)}")
                processed_ids["mother"] = post_filtered_patient(mapped_mother, token).get("id")
            except Exception as e:
                logger.error(f"Error processing MOTHER data: {str(e)}")

        # Post the Group resource
        try:
            post_family_group(processed_ids, token)
            logger.info("Successfully posted Group resource.")
        except Exception as e:
            logger.error(f"Error posting Group resource: {str(e)}")


        # Log or return IDs for further processing if needed
        logger.info(f"Processed IDs - CHILD: {child_id}, FATHER: {father_id}, MOTHER: {mother_id}")

        return Response({"message": "Event received and processed successfully."}, status=status.HTTP_200_OK)
