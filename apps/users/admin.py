from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "level_estimate", "target_score", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("NeuroEGE", {"fields": ("level_estimate", "stress_level", "target_score")}),
    )
