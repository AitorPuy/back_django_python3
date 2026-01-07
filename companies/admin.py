from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_primary", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    list_filter = ("is_primary",)
