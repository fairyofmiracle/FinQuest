from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('topic/<int:topic_id>/', views.topic_levels, name='topic_levels'),
    path('level/<int:level_id>/', views.level_play, name='level_play'),
]