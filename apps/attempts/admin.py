from django.contrib import admin

from .models import AIAnalysis, Attempt


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_type", "is_correct", "created_at")
    list_filter = ("is_correct", "content_type", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ("attempt", "algorithm_type", "confidence_score", "created_at")
    list_filter = ("algorithm_type",)
    readonly_fields = ("created_at", "updated_at")
