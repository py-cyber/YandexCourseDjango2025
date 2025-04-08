from datetime import timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, FormView, ListView, UpdateView


from users.forms import ProfileForm, SignUpForm
from users.models import User


class SignUpView(FormView):
    template_name = 'users/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = settings.DEFAULT_USER_IS_ACTIVE
        user.save()
        activation_link = f'http://{self.request.get_host()}/activate/{user.username}/'
        send_mail(
            _('Account activate'),
            _('Follow to link for activate: %(link)') % {'link': activation_link},
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class ActivateView(View):
    def get(self, username):
        user = User.objects.get(username=username)
        if timezone.now() - user.date_joined < timedelta(hours=12):
            user.is_active = True
            user.save()
            return redirect('login')

        return render(self.request, 'users/activation_expired.html')


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        users = User.objects.user_list().order_by('profile__score')[::-1]

        users_num = []
        current_num = 1
        prev_score = None

        for index, user in enumerate(users, start=1):
            if user.profile.score != prev_score:
                current_num = index
                prev_score = user.profile.score

            user.num = current_num
            users_num.append(user)

        return users_num


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['score'] = self.get_object().score
        return context
