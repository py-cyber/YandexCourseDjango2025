from django.contrib.auth import get_user_model
import django.db.models

from problems.models import Problem


User = get_user_model()


class Submission(django.db.models.Model):
    VERDICT_CHOICES = [
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('TLE', 'Time Limit Exceeded'),
        ('MLE', 'Memory Limit Exceeded'),
        ('RE', 'Runtime Error'),
        ('CE', 'Compilation Error'),
    ]

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
        choices=VERDICT_CHOICES,
        default='QU',
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
