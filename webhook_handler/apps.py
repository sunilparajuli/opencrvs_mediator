from django.apps import AppConfig
from webhook_handler.utils.openhim_mediator_config import *
from webhook_handler.utils.openhim_intercepter import *
from apscheduler.schedulers.background import BackgroundScheduler


class WebhookHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webhook_handler'

    def ready(self):
        #pass
        register_mediator()
        #scheduler = BackgroundScheduler()
        #interval_seconds =  3600  # Default to 10 seconds if not set

        #Schedule the heartbeat function
        #scheduler.add_job(send_heartbeat, 'interval', seconds=interval_seconds)
        #scheduler.start() 