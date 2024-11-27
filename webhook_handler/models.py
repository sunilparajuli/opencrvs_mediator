from django.db import models

class Subscription(models.Model):
    topic = models.CharField(max_length=255)
    callback_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription to {self.topic}"

class WebhookEvent(models.Model):
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()  # stores the full event data
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Event: {self.event_type} at {self.received_at}"