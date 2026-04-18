from django.contrib import admin

from accounts.models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content", "created_at", "is_processed", "user")
    list_filter = ("is_processed", "created_at")
    search_fields = ("title", "content", "user__username",)
