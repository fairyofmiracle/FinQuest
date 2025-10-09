from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from .models import User  # твой кастомный User
from game.models import Topic, UserLevelProgress

@login_required
def profile(request):
    user = request.user
    topics = Topic.objects.prefetch_related('level_set').all()
    for topic in topics:
        total = topic.level_set.count()
        completed = UserLevelProgress.objects.filter(
            user=user,
            level__topic=topic,
            completed=True
        ).count()
        topic.progress = {
            'completed': completed,
            'total': total,
            'percent': int(completed / total * 100) if total > 0 else 0
        }
    return render(request, 'accounts/profile.html', {
        'topics': topics,
    })

class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard')  # после регистрации — в дашборд

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # автоматический вход
        messages.success(self.request, "Регистрация прошла успешно! Добро пожаловать в FinQuest!")
        return redirect(self.success_url)