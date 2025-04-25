from django.contrib.auth import get_user_model
import django.db.models
from django.utils.translation import gettext_lazy as _

import problems.models


User = get_user_model()


class SubmissionManager(django.db.models.Manager):
    def get_full_submit(self, pk):
        return self.select_related('problem', 'user', 'test_error').get(pk=pk)


class Submission(django.db.models.Model):
    objects = SubmissionManager()

    user = django.db.models.ForeignKey(
        to=User,
        on_delete=django.db.models.CASCADE,
    )
    contest = django.db.models.ForeignKey(
        to='contests.Contest',
        on_delete=django.db.models.SET_NULL,
        null=True,
        blank=True,
        related_name='submissions',
    )
    problem = django.db.models.ForeignKey(
        to=problems.models.Problem,
        on_delete=django.db.models.CASCADE,
    )
    code = django.db.models.TextField()
    language = django.db.models.CharField(
        max_length=20,
    )
    verdict = django.db.models.CharField(
        choices=problems.models.VerdictChoice,
        default=problems.models.VerdictChoice.In_queue,
    )

    test_error = django.db.models.ForeignKey(
        problems.models.TestCase,
        null=True,
        on_delete=django.db.models.SET_NULL,
        default=None,
    )

    logs = django.db.models.TextField(
        verbose_name=_('logs'),
        blank=True,
        null=True,
    )

    submitted_at = django.db.models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-submitted_at']
