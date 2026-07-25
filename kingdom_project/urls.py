# kingdom_project/urls.py (Master Project Configuration)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Hooks your core application links to the homepage root
]

# ⚡ DEVELOPMENT MEDIA STREAM ROUTER: Serves user uploaded images locally
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
