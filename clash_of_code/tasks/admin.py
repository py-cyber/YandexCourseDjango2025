import django.contrib.admin

import tasks.models


@django.contrib.admin.register(tasks.models.Task)
class TaskAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        tasks.models.Task.name.field.name,
        tasks.models.Task.author.field.name,
        tasks.models.Task.is_public.field.name,
        tasks.models.Task.difficult.field.name,
    )

    filter_horizontal = (
        tasks.models.Task.tags.field.name,
    )

    list_editable = (
        tasks.models.Task.is_public.field.name,
    )

    list_display_links = (
        tasks.models.Task.name.field.name,
    )
