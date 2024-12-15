from django.contrib import admin
from .models import Configuration, Subscription

@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'webhook_url')
    fieldsets = (
        ('API Credentials', {
            'fields': ('client_id', 'client_secret', 'sha_secret', 'webhook_url', 'auth_url')
        }),
    )

    def has_add_permission(self, request):
        # Only allow adding if there's no configuration in the database
        return not Configuration.objects.exists()

admin.site.register(Subscription)