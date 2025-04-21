from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
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
        activation_link = (
            f'http://{self.request.get_host()}/users/activate/{user.username}/'
        )
        send_mail(
            _('Account activate'),
            _('Follow to link for activate: %(link)s') % {'link': activation_link},
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(
            self.request,
            _(
                'A confirmation email has been'
                ' sent to %(email)s. Please check your inbox.',
            )
            % {'email': user.email},
        )
        return super().form_valid(form)


class ActivateView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        if timezone.now() - user.date_joined < timedelta(hours=12):
            user.is_active = True
            user.save()
            return redirect('login')

        return render(request, 'users/activation_expired.html')


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return (
            User.objects.user_list()
            .select_related('profile')
            .only('username', 'date_joined', 'profile__image', 'profile__score')
            .order_by('-profile__score')
        )


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'profile_user'


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        context['score'] = profile.score
        return context
