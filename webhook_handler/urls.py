from django.urls import path
from webhook_handler.views import SubscriptionView, WebhookEventView

urlpatterns = [
    path('subscribe/', SubscriptionView.as_view(), name='subscribe'),
    path('webhooks/', WebhookEventView.as_view(), name='webhooks'),
]
