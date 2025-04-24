from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DuelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'duels'
    verbose_name = _('duels')
