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



class Configuration(models.Model):
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    sha_secret = models.CharField(max_length=255, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    auth_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "System Configuration (Single Row Only)"

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configuration"
