from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.story_list_view, name='list'),
    path('<slug:slug>/', views.story_detail_view, name='detail'),
]
