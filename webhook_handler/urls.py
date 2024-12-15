from django.urls import path
from webhook_handler.views import SubscriptionView, WebhookEventView
from .views import *

urlpatterns = [
    path('subscribe/', SubscriptionView.as_view(), name='subscribe'),
    path('webhooks/', WebhookEventView.as_view(), name='webhooks'),
    path('delete-webhooks/', DeleteWebHooksAPIView.as_view(), name='delete-webhooks'),

]
