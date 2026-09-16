"""
Bhromonghuri URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom Admin branding
admin.site.site_header = "🪁 ভ্রমণঘুড়ি — Admin Control Center"
admin.site.site_title = "Bhromonghuri Admin"
admin.site.index_title = "Dashboard & Website Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('tours/', include('apps.tours.urls', namespace='tours')),
    path('bookings/', include('apps.bookings.urls', namespace='bookings')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('stories/', include('apps.stories.urls', namespace='stories')),
    path('gallery/', include('apps.gallery.urls', namespace='gallery')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
