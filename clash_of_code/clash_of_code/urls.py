import django.conf
from django.conf.urls.static import static
from django.contrib import admin
import django.urls

urlpatterns = [
    django.urls.path('admin/', admin.site.urls),
    django.urls.path('tinymce/', django.urls.include('tinymce.urls')),
    django.urls.path('users/', django.urls.include('users.urls')),
    django.urls.path('problems/', django.urls.include('problems.urls')),
    django.urls.path('i18n/', django.urls.include('django.conf.urls.i18n')),
    django.urls.path(
        'contests/',
        django.urls.include('contests.urls', namespace='contests'),
    ),
    django.urls.path('', django.urls.include('homepage.urls')),
]

if django.conf.settings.DEBUG:
    import debug_toolbar.toolbar

    urlpatterns += debug_toolbar.toolbar.debug_toolbar_urls()

    urlpatterns += static(
        django.conf.settings.STATIC_URL,
        document_root=django.conf.settings.STATIC_ROOT,
    )
    urlpatterns += static(
        django.conf.settings.MEDIA_URL,
        document_root=django.conf.settings.MEDIA_ROOT,
    )
