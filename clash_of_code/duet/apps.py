from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DuetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'duet'
    verbose_name = _('Duet')
