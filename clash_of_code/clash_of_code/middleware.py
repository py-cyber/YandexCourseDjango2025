from django.contrib.auth import get_user_model


class OptimizedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user = (
                get_user_model()
                .objects.select_related(
                    'profile',
                )
                .prefetch_related(
                    'groups',
                    'user_permissions',
                )
                .get(pk=request.user.pk)
            )

        return self.get_response(request)
