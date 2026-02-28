# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from babybuddy import models


class SettingsInline(admin.StackedInline):
    model = models.Settings
    verbose_name = _("Settings")
    verbose_name_plural = _("Settings")
    can_delete = False
    fieldsets = (
        (
            _("Dashboard"),
            {
                "fields": (
                    "dashboard_refresh_rate",
                    "dashboard_hide_empty",
                    "dashboard_hide_age",
                )
            },
        ),
    )


class UserAdmin(BaseUserAdmin):
    inlines = (SettingsInline,)


class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "endpoint_short", "created_at")
    list_filter = ("user",)
    readonly_fields = ("created_at",)

    def endpoint_short(self, obj):
        return obj.endpoint[:60] + "..."
    endpoint_short.short_description = _("Endpoint")


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
admin.site.register(models.PushSubscription, PushSubscriptionAdmin)
