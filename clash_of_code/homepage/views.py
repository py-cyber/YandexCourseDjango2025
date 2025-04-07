from datetime import datetime, timedelta

from django.shortcuts import render


def home(request):
    template = 'homepage/home.html'

    show_banner = False
    if request.user.is_authenticated:
        user_log_date = datetime.now().date() - request.user.date_joined.date()
        show_banner = user_log_date < timedelta(days=3)

    context = {
        'show_banner': show_banner,
    }

    return render(request, template, context)
