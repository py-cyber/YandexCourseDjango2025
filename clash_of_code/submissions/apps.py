from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'submissions'
    verbose_name = _('Submissions')
