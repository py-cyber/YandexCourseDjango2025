from django.contrib.auth import get_user_model
import django.db.models
from django.utils.translation import gettext_lazy as _

import problems.models
from problems.models import Problem


User = get_user_model()


class VerdictChoice(django.db.models.TextChoices):
    Accept = 'AC', _('Accept')
    Compilation_error = 'CE', _('Compilation error')
    Wrong_answer = 'WA', _('Wrong answer')
    Time_limit = 'TL', _('Time limit')
    Runtime_error = 'RE', _('Runtime error')
    Memory_limit = 'ML', _('Memory limit')
    In_queue = 'IQ', _('In queue')
    In_processing = 'IP', _('In processing')


class Submission(django.db.models.Model):
    user = django.db.models.ForeignKey(
        to=User,
        on_delete=django.db.models.CASCADE,
    )
    problem = django.db.models.ForeignKey(
        to=Problem,
        on_delete=django.db.models.CASCADE,
    )
    code = django.db.models.TextField()
    language = django.db.models.CharField(
        max_length=20,
    )
    verdict = django.db.models.CharField(
        max_length=3,
        choices=VerdictChoice,
        default='IQ',
    )

    test_error = django.db.models.ForeignKey(
        problems.models.TestCase,
        null=True,
        on_delete=django.db.models.SET_NULL,
        default=None,
    )

    time_taken = django.db.models.FloatField(
        null=True,
        blank=True,
    )
    memory_used = django.db.models.FloatField(
        null=True,
        blank=True,
    )
    submitted_at = django.db.models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-submitted_at']
