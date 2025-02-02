from django.urls import path
from webhook_handler.views import  WebhookEventView
from webhook_handler.subscription import SubscriptionView, ListAppWebhooksAPIView, DeleteWebHooksAPIView

from .views import *

urlpatterns = [
    path('subscribe/', SubscriptionView.as_view(), name='subscribe'),
    path('webhooks/', WebhookEventView.as_view(), name='webhooks'),
    path('delete-webhooks/', DeleteWebHooksAPIView.as_view(), name='delete-webhooks'),
    path('list-webhooks/', ListAppWebhooksAPIView.as_view(), name='list-webhooks'),
]
#openHIM interactive routes for fhir interactions
urlpatterns +=[
    path('api/fhir/patient/', SubscriptionView.as_view(), name='subscribe'),
]
