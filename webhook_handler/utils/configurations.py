import os
from webhook_handler.models import Configuration

def get_configuration():
    config = Configuration.objects.first()  # Fetch the only row if it exists
    if config:
        return {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "sha_secret": config.sha_secret,
            "webhook_url": config.webhook_url,
            "auth_url" : config.auth_url #auth to crvs webhook ,http://localhost:4040/token
        }
    else:
        # Fallback to .env
        return {
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv('CLIENT_SECRET'),
            "sha_secret": os.getenv('SHA_SECRET'),
            "webhook_url": os.getenv('WEBHOOK_URL'),
            "auth_url": os.getenv('WEBHOOK_URL'),
        }
