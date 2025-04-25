from django.contrib.auth import get_user_model


class OptimizedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_queryset = (
                get_user_model()
                .objects.select_related('profile')
                .filter(is_active=True)
                .prefetch_related('groups', 'user_permissions')
            )
            request.user = user_queryset.get(pk=request.user.pk)

        return self.get_response(request)
