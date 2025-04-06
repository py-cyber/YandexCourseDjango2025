from django.contrib import admin
import django.urls

urlpatterns = [
    django.urls.path('admin/', admin.site.urls),
    django.urls.path('tinymce/', django.urls.include('tinymce.urls')),
]
