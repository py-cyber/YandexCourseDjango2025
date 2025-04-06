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

    filter_horizontal = (tasks.models.Task.tags.field.name,)

    list_editable = (tasks.models.Task.is_public.field.name,)

    list_display_links = (tasks.models.Task.name.field.name,)


@django.contrib.admin.register(tasks.models.Tag)
class TagAdmin(django.contrib.admin.ModelAdmin):
    list_display = (tasks.models.Tag.name.field.name,)

    list_display_links = (tasks.models.Tag.name.field.name,)


@django.contrib.admin.register(tasks.models.TestCase)
class TestAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'task_name',
        tasks.models.TestCase.visible.field.name,
    )

    list_editable = (tasks.models.TestCase.visible.field.name,)

    @django.contrib.admin.display(empty_value='???')
    def task_name(self, obj):
        return obj.task.name[:20]


@django.contrib.admin.register(tasks.models.Solution)
class SolutionsAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'task_name',
        'user_name',
        tasks.models.Solution.status.field.name,
        tasks.models.Solution.test_error.field.name,
    )

    @django.contrib.admin.display(empty_value='???')
    def task_name(self, obj):
        return obj.task.name[:20]

    @django.contrib.admin.display(empty_value='???')
    def user_name(self, obj):
        return obj.user.username[:20]
