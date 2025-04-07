from django.contrib import admin
from contests.models import Contest


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = (
        Contest.name.field.name,
        Contest.start_time.field.name,
        Contest.end_time.field.name,
        Contest.is_public.field.name,
        Contest.created_by.field.name,
    )
    list_filter = (
        Contest.is_public.field.name,
        Contest.start_time.field.name,
    )
    search_fields = (
        Contest.name.field.name,
        Contest.description.field.name,
    )
