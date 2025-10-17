from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta  # ← добавлен timedelta
from .models import (
    Topic, Level, UserLevelProgress, Article, Streak,
    Achievement, UserAchievement, Hint, Notification  # ← добавлен Notification
)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # ← редирект
    return render(request, 'game/home.html')

@login_required
def dashboard(request):
    user = request.user
    # Оптимизация: один запрос для всех данных
    topics = Topic.objects.prefetch_related('level_set').all()
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    
    # Получаем все прогрессы пользователя одним запросом
    user_progress = UserLevelProgress.objects.filter(user=user, completed=True).values_list('level__topic_id', flat=True)
    progress_counts = {}
    for topic_id in user_progress:
        progress_counts[topic_id] = progress_counts.get(topic_id, 0) + 1
    
    for topic in topics:
        total = topic.level_set.count()
        completed = progress_counts.get(topic.id, 0)
        topic.progress = {
            'percent': int(completed / total * 100) if total > 0 else 0
        }
    return render(request, 'game/dashboard.html', {'topics': topics, 'unread_notifications': unread_notifications})

@login_required
def media(request):
    articles = Article.objects.select_related('topic').order_by('-created_at')
    return render(request, 'game/media.html', {'articles': articles})

@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'game/article_detail.html', {'article': article})

@login_required
def topic_levels(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    levels = Level.objects.filter(topic=topic).order_by('order_in_topic')
    
    # Оптимизация: получаем все прогрессы одним запросом
    level_ids = [level.id for level in levels]
    existing_progress = UserLevelProgress.objects.filter(
        user=request.user, 
        level_id__in=level_ids
    ).select_related('level')
    
    progress_dict = {p.level_id: p for p in existing_progress}
    
    for level in levels:
        if level.id in progress_dict:
            level.user_progress = progress_dict[level.id]
        else:
            # Создаем новый прогресс только при необходимости
            level.user_progress = UserLevelProgress(
                user=request.user,
                level=level,
                completed=False,
                score=0,
                attempts=0
            )
    
    return render(request, 'game/topic_levels.html', {
        'topic': topic,
        'levels': levels,
    })

@login_required
def level_play(request, level_id):
    level = get_object_or_404(Level, id=level_id)
    # Подсказки: показываем, если куплена в этой сессии
    hint = Hint.objects.filter(level=level).first()
    session_key = f"hint_shown_{level.id}"

    if request.method == "POST" and request.POST.get("action") == "buy_hint":
        if not hint:
            messages.info(request, "Для этого уровня нет подсказок.")
            return redirect('level_play', level_id=level.id)
        if request.session.get(session_key):
            messages.info(request, "Подсказка уже открыта.")
            return redirect('level_play', level_id=level.id)
        if request.user.coins < hint.cost_coins:
            messages.error(request, "Недостаточно монет для подсказки.")
            return redirect('level_play', level_id=level.id)
        # Списываем монеты и открываем подсказку в рамках сессии
        request.user.coins -= hint.cost_coins
        request.user.save()
        request.session[session_key] = True
        messages.success(request, f"Подсказка открыта (-{hint.cost_coins} 🪙)")
        return redirect('level_play', level_id=level.id)
    if request.method == "POST":
        selected_option_id = request.POST.get("answer")
        if not selected_option_id:
            messages.error(request, "Выберите вариант ответа!")
            return redirect('level_play', level_id=level.id)

        selected_option = get_object_or_404(level.options, id=selected_option_id)
        is_correct = selected_option.is_correct

        progress, _ = UserLevelProgress.objects.get_or_create(
            user=request.user,
            level=level,
            defaults={'attempts': 0}
        )
        progress.attempts += 1

        if is_correct and not progress.completed:
            request.user.points += level.reward_points
            request.user.coins += level.reward_coins
            request.user.save()
            progress.completed = True
            progress.score = 100
        elif is_correct:
            progress.score = 100
        else:
            progress.score = 0

        # Обновляем лучшую попытку
        if progress.score is not None:
            progress.best_score = max(progress.best_score or 0, progress.score)

        progress.save()
        return redirect('level_result', level_id=level.id)

    return render(request, 'game/level_play.html', {
        'level': level,
        'options': level.options.all(),
        'hint': hint,
        'hint_shown': bool(request.session.get(session_key)),
    })

@login_required
def level_result(request, level_id):
    level = get_object_or_404(Level, id=level_id)
    progress = get_object_or_404(UserLevelProgress, user=request.user, level=level)
    correct_option = level.options.filter(is_correct=True).first()
    next_level = Level.objects.filter(
        topic=level.topic,
        order_in_topic__gt=level.order_in_topic
    ).first()

    # 🔥 Вызываем систему серий и достижений
    update_streak(request.user)
    check_achievements(request.user)

    return render(request, 'game/level_result.html', {
        'level': level,
        'progress': progress,
        'correct_option': correct_option,
        'next_level': next_level,
    })

# --- Вспомогательные функции ---

def check_achievements(user):
    for topic in Topic.objects.all():
        total = topic.level_set.count()
        completed = UserLevelProgress.objects.filter(
            user=user, level__topic=topic, completed=True
        ).count()
        if total > 0 and completed == total:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"Мастер {topic.name}",
                defaults={"description": f"Пройдены все уровни по теме «{topic.name}»"}
            )
            ua, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created and getattr(user, 'notifications_enabled', True):
                Notification.objects.create(
                    user=user,
                    text=f"Получено достижение: {achievement.name}"
                )

def update_streak(user):
    streak, _ = Streak.objects.get_or_create(user=user)
    today = date.today()
    if streak.last_activity == today:
        return
    elif streak.last_activity == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        # Разрыв серии
        if streak.last_activity is not None and getattr(user, 'notifications_enabled', True):
            Notification.objects.create(
                user=user,
                text="Серия прервана. Вернись в игру, чтобы начать новую!"
            )
        streak.current_streak = 1
    streak.last_activity = today
    streak.save()


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "Уведомления отмечены как прочитанные")
        return redirect('notifications')
    return render(request, 'game/notifications.html', {'notifications': notifications})


