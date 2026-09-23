from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('new/', views.booking_create_view, name='create'),
    path('success/<str:reference>/', views.booking_success_view, name='success'),
    path('lookup/', views.booking_lookup_view, name='lookup'),
    path('voucher/<str:reference>/pdf/', views.download_voucher_pdf_view, name='download_voucher'),
    path('<str:reference>/select-seats/', views.booking_select_seats_view, name='select_seats'),
    path('<str:reference>/seats-data/', views.booking_seat_map_api, name='seats_data'),
    path('<str:reference>/seat-map-api/', views.booking_seat_map_api, name='seat_map_api'),
]
