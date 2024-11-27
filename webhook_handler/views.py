from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from webhook_handler.utils.crvs_to_imis_converter import map_fhir_to_openimis
import requests
import logging
from webhook_handler.utils.crvs_auth_token import get_opencrvs_auth_token
from webhook_handler.utils.configurations import get_configuration
from .models import *
logger = logging.getLogger(__name__)



class SubscriptionView(APIView):
    def post(self, request):
        data = request.data
        config = get_configuration()
        if not config["webhook_url"]:
            return Response({"error": "Webhook URL not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        callback_url = data.get('callback_url', config["webhook_url"])
        try:
            auth_token = get_opencrvs_auth_token(config["client_id"], config["client_secret"], config['auth_url'])
            response = requests.post(
                config["webhook_url"],
                json={
                    'hub': {
                        'callback': callback_url,
                        'mode': 'subscribe',
                        'secret': config["sha_secret"],
                        'topic': data.get('topic')
                    }
                },
                headers={
                    'Authorization': f'Bearer {auth_token}',
                    'Content-Type': 'application/json'
                }
            )
            if response.status_code in [200,202]:
                return Response({}, status=status.HTTP_202_ACCEPTED)
            else:
                logger.error(f"Subscription failed: {response.content}")
                return Response({"error": "Failed to subscribe"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error during subscription: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class WebhookEventView(APIView):
    def post(self, request):
        # Log the incoming payload
        logger.info(f"Received webhook payload: {request.data}")

        # Map the FHIR data to OpenIMIS format using the utility function
        # mapped_data, error = map_fhir_to_openimis(request.data)
        # if error:
        #     return Response({"error": error}, status=400)

        # Save the mapped data (or just log it for now)
        # logger.info(f"Mapped data: {mapped_data}")
        # print("mapped_data_to_imis", mapped_data)
        # Save the event to the database if required (you can modify this to save specific data)
        # Assuming WebhookEvent model exists and has a `payload` field for storing the mapped data
        #event_type = request.data.get('event', {}).get('hub', {}).get('topic')
        # webhook_event = WebhookEvent.objects.create(
        #     event_type=event_type,
        #     payload=request.data  # Optionally, you can save the mapped_data instead
        # )
        print(request.data)
        return Response({"message": f"Event received and processed successfully"}, status=200)
