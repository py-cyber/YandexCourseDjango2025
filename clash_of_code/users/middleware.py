from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin

from users.models import User


class CustomUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                request.user = User.objects.get(pk=request.user.pk)

            except ObjectDoesNotExist:
                from django.contrib.auth import logout

                logout(request)
                return None

        return self.get_response(request)


__all__ = []
