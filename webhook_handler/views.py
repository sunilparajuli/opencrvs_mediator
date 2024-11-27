from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Subscription
from webhook_handler.serializers.serializers import SubscriptionSerializer
from webhook_handler.utils.crvs_to_imis_converter import map_fhir_to_openimis
import requests
import logging

logger = logging.getLogger(__name__)

class SubscriptionView(APIView):
    def post(self, request):
        data = request.data
        print("data", request.data)
        #serializer = SubscriptionSerializer(data=request.data)
        if True: #or serializer.is_valid():
            #subscription = serializer.save()
            #print(subscription.__dict__)
            # Subscribe to OpenCRVS here using requests
            try:
                import pdb;pdb.set_trace()
                auth_token = self.get_opencrvs_auth_token()  # Call your auth token function
                response = requests.post(
                    'http://localhost:2525/webhooks',  # Replace with actual OpenCRVS webhook URL
                    json={
                        'hub': {
                            'callback': data.get('callback_url'),#subscription.callback_url,
                            'mode': 'subscribe',
                            'secret': 'b15e2dab-6362-408b-b3b9-e8d76e77ac22',  # Shared secret for security
                            'topic': data.get('topic')#subscription.topic
                        }
                    },
                    headers={
                        'Authorization': f'Bearer {auth_token}',
                        'Content-Type': 'application/json'
                    }
                )
                if response.status_code == 200:
                    logger.info('Subscription successful')
                    print("success", response.json())
                    #return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                    pass
                else:
                    return Response({"error": "Failed to subscribe"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error during subscription: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_opencrvs_auth_token(self):
        from webhook_handler.utils.utils import get_opencrvs_auth_token
        token = get_opencrvs_auth_token()
        return token




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

        return Response({"message": "Event received and processed successfully"}, status=200)
