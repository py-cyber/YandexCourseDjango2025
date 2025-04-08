import sys

import django.contrib.auth.models
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    AuthUser._meta.get_field('email')._unique = True


class UserManager(django.contrib.auth.models.UserManager):
    def active(self):
        return self.filter(is_active=True)

    def by_mail(self, email):
        return self.filter(email=email)

    def with_profile(self):
        return self.select_related('profile')

    def user_list(self):
        return (
            self.active()
            .only(
                'username',
                'email',
                'profile__score',
            )
            .order_by('profile__score')
        )


class User(AuthUser):
    objects = UserManager()

    class Meta:
        proxy = True


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name='аватарка',
    )
    score = models.IntegerField(default=0, verbose_name='количество очков')

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=AuthUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=AuthUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_save, sender=AuthUser)
def validate_unique_email(sender, instance, **kwargs):
    if AuthUser.objects.filter(email=instance.email).exclude(pk=instance.pk).exists():
        raise ValidationError('Пользователь с таким email уже существует.')
