import importlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProblemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'problems'
    verbose_name = _('Problems')

    def ready(self):
        importlib.import_module('problems.signals')
