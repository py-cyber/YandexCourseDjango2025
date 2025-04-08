from datetime import timedelta

from django.utils import timezone
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'homepage/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        show_banner = False
        if self.request.user.is_authenticated:
            user_log_date = timezone.now().date() - self.request.user.date_joined.date()
            show_banner = user_log_date < timedelta(days=3)

        context['show_banner'] = show_banner
        return context
