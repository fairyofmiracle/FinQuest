# accounts/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logged_out.html'), name='logout'),
    path('logged_out/', auth_views.LogoutView.as_view(template_name='accounts/logged_out.html'), name='logged_out'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('reset/', views.reset_progress, name='reset_progress'),
]