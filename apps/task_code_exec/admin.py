from django.contrib import admin

from .models import CodeExecTask


@admin.register(CodeExecTask)
class CodeExecTaskAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "difficulty", "time_limit")
    list_filter = ("number", "difficulty")
    search_fields = ("title", "statement")
