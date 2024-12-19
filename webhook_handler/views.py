from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import logging
from webhook_handler.utils.crvs_auth_token import get_opencrvs_auth_token
from webhook_handler.utils.configurations import get_configuration
from webhook_handler.utils.crvs_to_imis_converter import map_patient_data
from .models import *
from django.shortcuts import render
import json
from django.conf import settings
from webhook_handler.utils.get_imis_auth_token import get_bearer_token
logger = logging.getLogger(__name__)



def webhook_manager(request):
    return render(request, 'index.html')



def post_filtered_patient(filtered_patient, token):
    post_url = f"{settings.OPENIMIS_FHIR_PATIENT_URL}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(post_url, headers=headers, json=filtered_patient)
    if response.status_code == 201:
        logger.info("Successfully posted the patient data.")
    else:
        # print(f"response data", response)
        logger.error(f"Failed to post patient data, status code: {response.status_code}, response: {response.text}")



class WebhookEventView(APIView):
    def post(self, request):
        entries = request.data.get("event", {}).get("context", [])[0].get("entry", [])
        if not entries:
            logger.error("No entries found in webhook payload.")
            return Response({"message": "No Patient data found."}, status=400)

        patient_resources = [
            entry["resource"] for entry in entries if entry.get("resource", {}).get("resourceType") == "Patient"
        ]

        if not patient_resources:
            logger.error("No Patient resources found in the payload.")
            return Response({"message": "No Patient resources found."}, status=400)
        token = get_bearer_token()
        
        if  token:        
            for idx, patient_resource in enumerate(patient_resources):
                try:
                    is_head = idx == 0  # Set True for the first patient only
                    mapped_patient = map_patient_data(patient_resource, is_head=is_head)
                    print(json.dumps(mapped_patient))
                    # logger.info(f"Mapped patient data: {json.dumps(mapped_patient)}")
                    post_filtered_patient(mapped_patient, token)  # Post each patient to API
                except Exception as e:
                    logger.error(f"Error processing patient data: {str(e)}")

        return Response({"message": f"Event received and processed successfully"}, status=200)







