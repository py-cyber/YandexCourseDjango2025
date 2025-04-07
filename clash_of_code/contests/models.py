from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


User = get_user_model()


class Contest(models.Model):
    name = models.CharField(
        max_length=200,
    )
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(
        default=False,
    )
    registration_open = models.BooleanField(
        default=True,
    )
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
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
