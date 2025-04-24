import django.db.models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from gevent.libev.corecext import child

User = get_user_model()


class StatusGameChoice(django.db.models.TextChoices):
    finished = 'finished', _('Finished')
    running = 'running', _('Running')


class Room(django.db.models.Model):
    player1 = django.db.models.ForeignKey(
        to=User,
        verbose_name=_('player 1'),
        on_delete=django.db.models.CASCADE,
        related_name='player1',
    )

    player2 = django.db.models.ForeignKey(
        to=User,
        verbose_name=_('player 2'),
        on_delete=django.db.models.CASCADE,
        related_name='player2',
    )

    status = django.db.models.CharField(
        verbose_name=_('status game'),
        choices=StatusGameChoice,
        default=StatusGameChoice.running,
    )

    round = django.db.models.PositiveIntegerField(
        verbose_name=_('round count'),
        default=1,
    )

    winner = django.db.models.ForeignKey(
        to=User,
        verbose_name=_('winner in game'),
        on_delete=django.db.models.CASCADE,
        blank=True,
        null=True,
        default=True,
    )

class ManagerWaitingPlayers(django.db.models.Manager):
    def sr(self):
        return self.select_related('user')

    def get_suitable_user(self, user):
        return (
            self.sr()
            .filter(
                user__profile__rating__gte=user.profile.rating - 150,
                user__profile__rating__lte=user.profile.rating + 150,
            )
            .order_by('-start_time')
        )


class StatusChoice(django.db.models.TextChoices):
    searching = 'searching', _('searching')
    confirm = 'confirm', _('confirm')


class WaitingPlayers(django.db.models.Model):
    objects = ManagerWaitingPlayers()

    user = django.db.models.ForeignKey(
        to=User,
        on_delete=django.db.models.CASCADE,
        help_text=_('Table of users waiting for the game'),
    )

    start_time = django.db.models.DateTimeField(
        verbose_name=_('search start time'),
        auto_now_add=True,
    )

    status = django.db.models.CharField(
        choices=StatusChoice,
    )
