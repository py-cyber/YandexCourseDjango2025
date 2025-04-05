from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from users.forms import ProfileForm, SignUpForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = settings.DEFAULT_USER_IS_ACTIVE
            user.save()
            activation_link = f'http://{request.get_host()}/activate/{user.username}/'
            send_mail(
                'Активация аккаунта',
                f'Перейдите по ссылке для активации: {activation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})


def activate(request, username):
    user = User.objects.get(username=username)
    if timezone.now() - user.date_joined < timedelta(hours=12):
        user.is_active = True
        user.save()
        return redirect('login')

    return render(request, 'users/activation_expired.html')


def user_list(request):
    users = User.objects.filter(is_active=True).only(
        'username',
        'email',
        'date_joined',
    )
    return render(request, 'users/user_list.html', {'users': users})


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/user_detail.html', {'user': user})


@login_required
def profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    score = profile.score

    return render(
        request,
        'users/profile.html',
        {
            'form': form,
            'score': score,
        },
    )


__all__ = []
