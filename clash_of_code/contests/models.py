from django.contrib.auth import get_user_model
import django.db.models
from django.utils import timezone


User = get_user_model()


class ContestManager(django.db.models.Manager):
    def is_public(self):
        return self.filter(is_public=True)


class Contest(django.db.models.Model):
    objects = ContestManager()
    name = django.db.models.CharField(
        max_length=200,
    )
    description = django.db.models.TextField()
    start_time = django.db.models.DateTimeField()
    end_time = django.db.models.DateTimeField()
    is_public = django.db.models.BooleanField(
        default=False,
    )
    registration_open = django.db.models.BooleanField(
        default=True,
    )
    created_by = django.db.models.ForeignKey(
        to=User,
        on_delete=django.db.models.CASCADE,
    )
    participants = django.db.models.ManyToManyField(
        to=User,
        through='ContestRegistration',
        related_name='contests_participated',
        blank=True,
    )

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'

        if self.start_time <= now <= self.end_time:
            return 'running'

        return 'finished'

    def __str__(self):
        return self.name


class ContestProblem(django.db.models.Model):
    contest = django.db.models.ForeignKey(
        to=Contest,
        on_delete=django.db.models.CASCADE,
    )
    problem = django.db.models.ForeignKey(
        to='problems.Problem',
        on_delete=django.db.models.CASCADE,
    )
    points = django.db.models.IntegerField(
        default=100,
    )
    order = django.db.models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['order']
        unique_together = ('contest', 'problem')


class ContestRegistration(django.db.models.Model):
    user = django.db.models.ForeignKey(
        to=User,
        on_delete=django.db.models.CASCADE,
    )
    contest = django.db.models.ForeignKey(
        to=Contest,
        on_delete=django.db.models.CASCADE,
    )
    registration_time = django.db.models.DateTimeField(
        auto_now_add=True,
    )
    is_approved = django.db.models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = ('user', 'contest')
