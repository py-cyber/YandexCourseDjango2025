import django.conf
from django.contrib import admin
import django.urls

urlpatterns = [
    django.urls.path('admin/', admin.site.urls),
    django.urls.path('tinymce/', django.urls.include('tinymce.urls')),
]

if django.conf.settings.DEBUG:
    import debug_toolbar.toolbar

    urlpatterns += debug_toolbar.toolbar.debug_toolbar_urls()
