from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from users.forms import CustomUserChangeForm
import users.models
from users.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = (
        users.models.Profile.image.field.name,
        users.models.Profile.score.field.name,
    )
    readonly_fields = (users.models.Profile.score.field.name,)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    form = CustomUserChangeForm


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

__all__ = []
