from django.contrib.auth import get_user_model
import django.db.models

User = get_user_model()


class Problem(django.db.models.Model):
    DIFFICULTY_CHOICES = [
        ('E', 'Easy'),
        ('M', 'Medium'),
        ('H', 'Hard'),
    ]

    title = django.db.models.CharField(
        max_length=200,
    )
    description = django.db.models.TextField()
    difficulty = django.db.models.CharField(
        max_length=1,
        choices=DIFFICULTY_CHOICES,
    )
    time_limit = django.db.models.IntegerField(
        default=1,
    )
    memory_limit = django.db.models.IntegerField(
        default=256,
    )
    created_at = django.db.models.DateTimeField(
        auto_now_add=True,
    )
    author = django.db.models.ForeignKey(
        to=User,
        on_delete=django.db.models.SET_NULL,
        null=True,
    )
    is_public = django.db.models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.title


class TestCase(django.db.models.Model):
    problem = django.db.models.ForeignKey(
        to=Problem,
        on_delete=django.db.models.CASCADE,
    )
    input_field = django.db.models.TextField(
        db_column='input',
        verbose_name='input',
    )
    output = django.db.models.TextField()
    is_sample = django.db.models.BooleanField(
        default=False,
    )
