from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<str:reference>/', views.checkout_view, name='checkout'),
    path('submit/<str:reference>/', views.submit_payment_view, name='submit'),
    path('pending/<str:reference>/', views.pending_verification_view, name='pending'),
    path('simulate/<str:reference>/', views.process_simulation_view, name='simulate'),
    path('webhook/', views.webhook_view, name='webhook'),
]
