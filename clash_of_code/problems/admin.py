import django.contrib.admin

import problems.models


@django.contrib.admin.register(problems.models.Problem)
class ProblemAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        problems.models.Problem.title.field.name,
        problems.models.Problem.author.field.name,
        problems.models.Problem.is_public.field.name,
        problems.models.Problem.difficult.field.name,
    )

    filter_horizontal = (problems.models.Problem.tags.field.name,)

    list_editable = (problems.models.Problem.is_public.field.name,)

    list_display_links = (problems.models.Problem.title.field.name,)


@django.contrib.admin.register(problems.models.Tag)
class TagAdmin(django.contrib.admin.ModelAdmin):
    list_display = (problems.models.Tag.name.field.name,)

    list_display_links = (problems.models.Tag.name.field.name,)


@django.contrib.admin.register(problems.models.TestCase)
class TestAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'problem_name',
        problems.models.TestCase.is_sample.field.name,
    )

    list_editable = (problems.models.TestCase.is_sample.field.name,)

    @django.contrib.admin.display(empty_value='???')
    def problem_name(self, obj):
        return obj.problem.title[:20]
