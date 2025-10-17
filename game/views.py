from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta  # ← добавлен timedelta
from .models import (
    Topic, Level, UserLevelProgress, Article, Streak,
    Achievement, UserAchievement, Hint, Notification, Leaderboard  # ← добавлен Leaderboard
)
from accounts.models import User  # ← добавлен импорт User

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
    
    # Проверяем, первый ли это вход пользователя
    # Пользователь считается новым, если у него нет прогресса по уровням
    has_progress = UserLevelProgress.objects.filter(user=user).exists()
    is_first_visit = not has_progress
    
    # Добавляем данные о прогрессе пользователя
    user.level_progress = user.get_level_progress()
    user.achievements_count = user.get_achievements_count()
    
    # Обновляем рейтинг пользователя
    update_leaderboard(user)
    
    return render(request, 'game/dashboard.html', {
        'topics': topics, 
        'unread_notifications': unread_notifications,
        'is_first_visit': is_first_visit
    })

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
    
    # Проверяем, что пользователь действительно существует в базе
    if not User.objects.filter(id=request.user.id).exists():
        messages.error(request, "Ошибка аутентификации. Пожалуйста, войдите заново.")
        return redirect('login')

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
        # Обрабатываем разные типы уровней
        is_correct = False
        user_answer = None
        
        if level.type == 'quiz':
            # Старая логика для квизов
            selected_option_id = request.POST.get("answer")
            if not selected_option_id:
                messages.error(request, "Выберите вариант ответа!")
                return redirect('level_play', level_id=level.id)
            selected_option = get_object_or_404(level.options, id=selected_option_id)
            is_correct = selected_option.is_correct
            user_answer = selected_option.text
            
        elif level.type in ['scenario', 'calculation', 'matching', 'sorting', 'simulation']:
            # Новая логика для других типов уровней
            is_correct, user_answer = process_level_answer(level, request.POST)

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

def process_level_answer(level, post_data):
    """Обрабатывает ответы для разных типов уровней"""
    content = level.content
    
    if level.type == 'scenario':
        # Обработка сценариев
        selected_option = int(post_data.get('scenario_answer', 0))
        correct_answer = content.get('correct_answer', 0)
        return selected_option == correct_answer, f"Выбрано: {selected_option + 1}"
    
    elif level.type == 'calculation':
        # Обработка расчетов
        user_answer = float(post_data.get('calculation_answer', 0))
        correct_answer = content.get('correct_answer', 0)
        tolerance = content.get('tolerance', 0)
        is_correct = abs(user_answer - correct_answer) <= tolerance
        return is_correct, f"Ответ: {user_answer}"
    
    elif level.type == 'matching':
        # Обработка сопоставления
        matches = []
        for key, value in post_data.items():
            if key.startswith('match_'):
                matches.append([int(key.split('_')[1]), int(value)])
        correct_matches = content.get('correct_matches', [])
        is_correct = sorted(matches) == sorted(correct_matches)
        return is_correct, f"Сопоставлений: {len(matches)}"
    
    elif level.type == 'sorting':
        # Обработка сортировки
        order = []
        for key, value in post_data.items():
            if key.startswith('sort_'):
                order.append(int(value))
        correct_order = content.get('correct_order', [])
        is_correct = order == correct_order
        return is_correct, f"Порядок: {order}"
    
    elif level.type == 'simulation':
        # Обработка симуляций
        response_index = int(post_data.get('simulation_response', 0))
        dialogue = content.get('dialogue', [])
        if dialogue and response_index < len(dialogue[0].get('responses', [])):
            response = dialogue[0]['responses'][response_index]
            is_correct = response.get('result') == 'win'
            return is_correct, response.get('message', '')
    
    return False, "Неизвестный тип уровня"

def update_leaderboard(user):
    """Обновляет рейтинг пользователя в турнирной таблице"""
    # Получаем статистику пользователя
    levels_completed = UserLevelProgress.objects.filter(user=user, completed=True).count()
    achievements_count = UserAchievement.objects.filter(user=user).count()
    
    # Получаем текущую серию
    try:
        streak = Streak.objects.get(user=user)
        streak_days = streak.current_streak
    except Streak.DoesNotExist:
        streak_days = 0
    
    # Создаем или обновляем запись в рейтинге
    leaderboard_entry, created = Leaderboard.objects.get_or_create(
        user=user,
        defaults={
            'total_points': user.points,
            'total_coins': user.coins,
            'levels_completed': levels_completed,
            'achievements_count': achievements_count,
            'streak_days': streak_days
        }
    )
    
    if not created:
        # Обновляем существующую запись
        leaderboard_entry.total_points = user.points
        leaderboard_entry.total_coins = user.coins
        leaderboard_entry.levels_completed = levels_completed
        leaderboard_entry.achievements_count = achievements_count
        leaderboard_entry.streak_days = streak_days
        leaderboard_entry.save()

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "Уведомления отмечены как прочитанные")
        return redirect('notifications_list')
    return render(request, 'game/notifications.html', {'notifications': notifications})

@login_required
def leaderboard(request):
    """Турнирная таблица игроков"""
    # Обновляем рейтинг текущего пользователя
    update_leaderboard(request.user)
    
    # Получаем топ-20 игроков
    top_players = Leaderboard.objects.select_related('user').all()[:20]
    
    # Получаем позицию текущего пользователя
    try:
        current_user_entry = Leaderboard.objects.get(user=request.user)
        current_user_rank = current_user_entry.get_rank()
    except Leaderboard.DoesNotExist:
        current_user_entry = None
        current_user_rank = None
    
    return render(request, 'game/leaderboard.html', {
        'top_players': top_players,
        'current_user_entry': current_user_entry,
        'current_user_rank': current_user_rank
    })


