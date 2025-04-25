from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        tz_name = request.session.get('django_timezone', settings.TIME_ZONE)
        try:
            timezone.activate(ZoneInfo(tz_name))
        except (ValueError, KeyError):
            timezone.activate(ZoneInfo(settings.TIME_ZONE))
