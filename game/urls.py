from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),                 # /
    path('media/', views.media, name='media'),                   # /media/
    path('media/<int:pk>/', views.article_detail, name='article_detail'),  # /media/1/
    path('topic/<int:topic_id>/', views.topic_levels, name='topic_levels'), # /topic/1/
    path('level/<int:level_id>/', views.level_play, name='level_play'),     # /level/1/
    path('level/<int:level_id>/result/', views.level_result, name='level_result'), # /level/1/result/
    path('notifications/', views.notifications_list, name='notifications'),  # /notifications/
]