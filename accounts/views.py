from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import User
from game.models import Topic, UserLevelProgress, UserAchievement


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

    achievements = UserAchievement.objects.filter(
        user=user
    ).select_related('achievement').order_by('-earned_at')[:6]

    return render(request, 'accounts/profile.html', {
        'topics': topics,
        'achievements': achievements,
        # 'user': user  # необязательно — уже доступен в шаблоне
    })


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['files'] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно! Добро пожаловать в FinQuest!")
        return redirect(self.success_url)

@login_required
def settings_view(request):
    if request.method == "POST":
        # Обработка аватара
        if 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']

        # Обработка уведомлений
        request.user.notifications_enabled = 'notifications' in request.POST
        request.user.save()
        messages.success(request, "Настройки сохранены!")
        return redirect('settings')

    return render(request, 'accounts/settings.html')


@login_required
def reset_progress(request):
    # Удаляем прогресс и достижения
    UserLevelProgress.objects.filter(user=request.user).delete()
    UserAchievement.objects.filter(user=request.user).delete()
    # Сбрасываем очки и монеты
    request.user.points = 0
    request.user.coins = 0
    request.user.level_number = 1
    request.user.save()
    messages.success(request, "Прогресс сброшен!")
    return redirect('profile')