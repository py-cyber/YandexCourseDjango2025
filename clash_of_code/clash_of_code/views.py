import http

from django.shortcuts import render
from django.views.generic import TemplateView


class Error404(TemplateView):
    template_name = 'errors/404.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = render(request, self.template_name, context)
        response.status_code = http.HTTPStatus.NOT_FOUND
        return response


class Error403(TemplateView):
    template_name = 'errors/403.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = render(request, self.template_name, context)
        response.status_code = http.HTTPStatus.FORBIDDEN
        return response


class Error500(TemplateView):
    template_name = 'errors/500.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        response = render(request, self.template_name, context)
        response.status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR
        return response
