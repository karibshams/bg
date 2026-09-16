from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('new/', views.booking_create_view, name='create'),
    path('success/<str:reference>/', views.booking_success_view, name='success'),
    path('lookup/', views.booking_lookup_view, name='lookup'),
]
