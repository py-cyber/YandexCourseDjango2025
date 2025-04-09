from django.db import models

from users.models import User


class ProgrammingLanguage(models.Model):
    name = models.CharField(
        max_length=50,
        default='python',
    )
    ace_mode = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CodeRoom(models.Model):
    name = models.CharField(max_length=100)
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.PROTECT)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField(User, related_name='participating_rooms')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_rooms',
    )

    def __str__(self):
        return f'{self.name} ({self.language})'


class RoomInvitation(models.Model):
    room = models.ForeignKey(CodeRoom, on_delete=models.CASCADE)
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invites',
    )
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_invites',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    def accept(self):
        self.room.participants.add(self.invitee)
        self.is_accepted = True
        self.save()

    class Meta:
        unique_together = ('room', 'invitee')

    def __str__(self):
        return f'Invite to {self.room} for {self.invitee}'
