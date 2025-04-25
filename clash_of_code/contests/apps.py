from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contests'
    verbose_name = _('Contests')
