from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Subscription
from webhook_handler.serializers.serializers import SubscriptionSerializer
import requests
import logging

logger = logging.getLogger(__name__)

class SubscriptionView(APIView):
    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            # Subscribe to OpenCRVS here using requests
            try:
                auth_token = self.get_opencrvs_auth_token()  # Call your auth token function
                response = requests.post(
                    'WEBHOOK_URL',  # Replace with actual OpenCRVS webhook URL
                    json={
                        'hub': {
                            'callback': subscription.callback_url,
                            'mode': 'subscribe',
                            'secret': 'SHA_SECRET',  # Shared secret for security
                            'topic': subscription.topic
                        }
                    },
                    headers={
                        'Authorization': f'Bearer {auth_token}',
                        'Content-Type': 'application/json'
                    }
                )
                if response.status_code == 200:
                    logger.info('Subscription successful')
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({"error": "Failed to subscribe"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error during subscription: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_opencrvs_auth_token(self):
        # Implement the token generation logic
        return "some_auth_token"  # This should be replaced with actual logic




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WebhookEvent
import logging

logger = logging.getLogger(__name__)

class WebhookEventView(APIView):
    def post(self, request):
        # Log the incoming payload
        logger.info(f"Received webhook payload: {request.data}")

        # Save the event to the database
        event_type = request.data.get('eventType')
        event_data = request.data.get('data')

        if event_type and event_data:
            webhook_event = WebhookEvent.objects.create(
                event_type=event_type,
                payload=event_data
            )
            logger.info(f"Event saved: {webhook_event}")
            return Response({"message": "Event received successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
