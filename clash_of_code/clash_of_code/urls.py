import django.conf
from django.contrib import admin
import django.urls

urlpatterns = [
    django.urls.path('admin/', admin.site.urls),
    django.urls.path('tinymce/', django.urls.include('tinymce.urls')),
    django.urls.path('users/', django.urls.include('users.urls')),
    django.urls.path('i18n/', django.urls.include('django.conf.urls.i18n')),
]

if django.conf.settings.DEBUG:
    import debug_toolbar.toolbar

    urlpatterns += debug_toolbar.toolbar.debug_toolbar_urls()
