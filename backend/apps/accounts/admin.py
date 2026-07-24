from django.contrib import admin

from apps.core.admin import playlytics_admin_site
from apps.accounts.models import User

@admin.register(User, site=playlytics_admin_site)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "favorite_team", "is_active", "is_superuser", "is_staff")
    ordering = ("username",)

    search_fields = ("username", "email")
    list_filter = ("is_active", "is_superuser", "is_staff")

    readonly_fields = ("id", "email", "password")
    fieldsets = (
        ("User Information", {
            "fields": ("username", "email", "password", "favorite_team")}),
        ("Permissions", {
            "fields": ("is_active", "is_superuser", "is_staff")}),
    )