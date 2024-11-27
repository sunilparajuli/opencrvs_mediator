from rest_framework import serializers
from webhook_handler.models import Subscription, WebhookEvent

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'topic', 'callback_url', 'created_at']

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_type', 'payload', 'received_at']
