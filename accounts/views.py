from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import User
from game.models import Topic, UserLevelProgress, UserAchievement, Achievement


@login_required
def profile(request):
    user = request.user
    
    # Группируем темы по категориям и считаем прогресс по категориям
    categories = {
        'basics': {'name': 'Основы финансов', 'icon': 'fa-piggy-bank', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
        'security': {'name': 'Безопасность', 'icon': 'fa-shield-halved', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
        'investments': {'name': 'Инвестиции', 'icon': 'fa-chart-line', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
        'planning': {'name': 'Планирование', 'icon': 'fa-bullseye', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
    }
    
    topics = Topic.objects.prefetch_related('level_set').all()
    for topic in topics:
        total = topic.level_set.count()
        completed = UserLevelProgress.objects.filter(
            user=user,
            level__topic=topic,
            completed=True
        ).count()
        
        # Подсчитываем правильные ответы для системы оценки по процентам
        correct_answers = UserLevelProgress.objects.filter(
            user=user,
            level__topic=topic,
            completed=True,
            score__gte=80  # 80% и выше считается успешным прохождением
        ).count()
        
        if topic.main_category in categories:
            categories[topic.main_category]['topics'].append(topic)
            categories[topic.main_category]['total_levels'] += total
            categories[topic.main_category]['completed_levels'] += correct_answers  # Используем правильные ответы
    
    # Вычисляем процент прогресса для каждой категории
    for category in categories.values():
        if category['total_levels'] > 0:
            category['progress_percent'] = int(category['completed_levels'] / category['total_levels'] * 100)
        else:
            category['progress_percent'] = 0

    # Получаем все достижения пользователя
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement').order_by('-earned_at')
    
    # Получаем все возможные достижения
    all_achievements = []
    
    # Добавляем системные достижения (не привязанные к темам)
    system_achievements = Achievement.objects.filter(
        name__in=['Первые шаги', 'Легенда финансовой грамотности']
    )
    
    for achievement in system_achievements:
        # Проверяем, получено ли достижение пользователем
        user_achievement = UserAchievement.objects.filter(
            user=user, achievement=achievement
        ).first()
        
        all_achievements.append({
            'achievement': achievement,
            'earned': user_achievement is not None,
            'earned_at': user_achievement.earned_at if user_achievement else None
        })
    
    # Добавляем достижения для тем с разными уровнями редкости
    rarity_levels = ['common', 'uncommon', 'rare', 'legendary']
    icon_classes = ['fa-solid fa-star', 'fa-solid fa-gem', 'fa-solid fa-trophy', 'fa-solid fa-crown']
    
    for index, topic in enumerate(Topic.objects.all()):
        achievement_name = f"Мастер {topic.name}"
        achievement_description = f"Пройдены все уровни по теме «{topic.name}»"
        
        # Определяем редкость в зависимости от индекса
        rarity_index = index % len(rarity_levels)
        rarity = rarity_levels[rarity_index]
        icon = icon_classes[rarity_index]
        
        # Получаем или создаем достижение с редкостью
        achievement, _ = Achievement.objects.get_or_create(
            name=achievement_name,
            defaults={
                "description": achievement_description,
                "rarity": rarity,
                "icon": icon
            }
        )
        
        # Если достижение уже существует без редкости, добавляем её
        if not achievement.rarity:
            achievement.rarity = rarity
            achievement.icon = icon
            achievement.save()
        
        # Проверяем, получено ли достижение пользователем
        user_achievement = UserAchievement.objects.filter(
            user=user, achievement=achievement
        ).first()
        
        all_achievements.append({
            'achievement': achievement,
            'earned': user_achievement is not None,
            'earned_at': user_achievement.earned_at if user_achievement else None
        })
    
    # Сортируем: сначала полученные, потом неполученные
    achievements = sorted(all_achievements, key=lambda x: (not x['earned'], x['achievement'].name))

    return render(request, 'accounts/profile.html', {
        'categories': categories,
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
        # Устанавливаем аватарку по умолчанию при регистрации
        user.default_avatar = 'default1'  # Монеты
        user.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно! Добро пожаловать в FinQuest!")
        return redirect(self.success_url)

@login_required
def settings_view(request):
    if request.method == "POST":
        # Обработка выбора готовой аватарки
        selected_avatar = request.POST.get('selected_avatar')
        if selected_avatar:
            # Устанавливаем аватарку по умолчанию
            request.user.avatar = None
            request.user.default_avatar = selected_avatar
        
        # Обработка загрузки собственного аватара
        if 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']
            request.user.default_avatar = None  # Сбрасываем выбор готовой аватарки

        # Обработка выбора рамки
        selected_border = request.POST.get('selected_border')
        if selected_border:
            request.user.avatar_border = selected_border

        # Обработка уведомлений
        request.user.notifications_enabled = 'notifications' in request.POST
        request.user.save()
        messages.success(request, "Настройки сохранены!")
        return redirect('profile')

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

def custom_logout(request):
    """Кастомный выход с показом страницы logged_out.html"""
    logout(request)
    return render(request, 'accounts/logged_out.html')