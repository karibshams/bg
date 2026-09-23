from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list_view, name='list'),
    path('corporate/<str:reference>/voucher/', views.corporate_voucher_view, name='corporate_voucher'),
    path('destination/<slug:slug>/', views.destination_detail_view, name='destination_detail'),
    path('<slug:slug>/', views.tour_detail_view, name='detail'),
]
