
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
import logging
logger = logging.getLogger(__name__)
from django.conf import settings

class SubscriptionView(APIView):
    def post(self, request):
        data = request.data
        topic = data.get("topic")
        if not topic:
            return Response(
                {"message": "Topic required BIRTH_REGISTERED or DEATH_REGISTERED"},
                status=status.HTTP_400_BAD_REQUEST,
            )              
        config = get_configuration()
        if not config["webhook_url"]:
            return Response({"error": "Webhook URL not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        callback_url = settings.CALLBACK_URL_OPENHIM#data.get('callback_url', config["webhook_url"])
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
                settings.SUBSCRIBE_WEBHOOK_THROUGH_OPENHIM,
                json={
                    'hub': {
                        'callback': "http://localhost:5001/post-openimis",#settings.CALLBACK_URL_OPENHIM,#callback_url,
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
            import pdb;pdb.set_trace()
            if response.status_code in [200,202]:
                Subscription.objects.create(topic=topic, callback_url=callback_url)
                return Response({"response": True}, status=status.HTTP_202_ACCEPTED)
            else:
                logger.error(f"Subscription failed: {response.content}")
                return Response({"error": f""}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error during subscription: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ListAppWebhooksAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            config = get_configuration()
            BASE_URL = settings.LIST_WEBHOOKS_URL
            auth_token = get_opencrvs_auth_token(config["client_id"], config["client_secret"], config['auth_url'])

            # Set headers and payload
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
            payload = {
                "hub": {
                    "callback": settings.CALLBACK_URL_OPENHIM,#"http://localhost:8000/api/webhooks/",
                    "mode": "subscribe",
                    "topic": "BIRTH_REGISTERED",
                    "secret": settings.SECRECT
                }
            }

            # Make the GET request to the webhook service
            response = requests.get(BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
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
            "callback": settings.CALLBACK_URL_OPENHIM,
            "mode": "subscribe",
            "topic": "BIRTH_REGISTERED",
            "secret": settings.SECRECT
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