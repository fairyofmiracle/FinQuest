from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),                 # /
    path('articles/', views.media, name='articles'),                   # /articles/
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),  # /articles/1/
    path('category/<str:category_slug>/', views.category_detail, name='category_detail'), # /category/basics/
    path('topic/<int:topic_id>/', views.topic_levels, name='topic_levels'), # /topic/1/
    path('level/<int:level_id>/', views.level_play, name='level_play'),     # /level/1/
    path('level/<int:level_id>/result/', views.level_result, name='level_result'), # /level/1/result/
    path('notifications/', views.notifications_list, name='notifications_list'),  # /notifications/
    path('daily-quests/', views.daily_quests, name='daily_quests'),  # /daily-quests/
    path('leaderboard/', views.leaderboard, name='leaderboard'),  # /leaderboard/
    path('mobile-achievements/', views.mobile_achievements, name='mobile_achievements'),  # /mobile-achievements/
    path('mobile-skills/', views.mobile_skills, name='mobile_skills'),  # /mobile-skills/
    path('categories/', views.categories, name='categories'),  # /categories/
    path('toggle-mobile/', views.toggle_mobile_view, name='toggle_mobile_view'),  # /toggle-mobile/
]