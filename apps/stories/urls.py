from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.story_list_view, name='list'),
    path('submit/', views.story_submit_view, name='submit'),
    path('moderate/<int:story_id>/<str:action>/', views.story_moderate_action, name='moderate'),
    path('<slug:slug>/', views.story_detail_view, name='detail'),
]
