from django.contrib import admin

from .models import KalabashInstance, KalabashExtension


class KalabashInstanceAdmin(admin.ModelAdmin):
    """Admin class for KalabashInstance model."""

    list_display = (
        "hostname", "known_version",
        "domain_counter", "domain_alias_counter",
        "mailbox_counter", "alias_counter",
        "created", "last_request",
    )
    list_filter = ("known_version", )
    search_fields = ["ip_address", "hostname"]


class KalabashExtensionAdmin(admin.ModelAdmin):

    """Admin class for KalabashExtension model."""

    list_display = ("name", "version")


admin.site.register(KalabashInstance, KalabashInstanceAdmin)
admin.site.register(KalabashExtension, KalabashExtensionAdmin)
