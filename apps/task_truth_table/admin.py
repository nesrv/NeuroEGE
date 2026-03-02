from django.contrib import admin

from .models import TruthTableTask


@admin.register(TruthTableTask)
class TruthTableTaskAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "expression", "difficulty")
    list_filter = ("difficulty",)
    search_fields = ("title", "expression")
