from django.contrib.admin import ModelAdmin, register


import duet.models


@register(duet.models.ProgrammingLanguage)
class ProgrammingLanguageAdmin(ModelAdmin):
    list_display = (
        duet.models.ProgrammingLanguage.name.field.name,
        duet.models.ProgrammingLanguage.ace_mode.field.name,
    )
    list_display_links = (duet.models.ProgrammingLanguage.name.field.name,)
