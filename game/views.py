from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Level, UserLevelProgress, Article
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def home(request):
    """Главная страница для всех (анонимных и залогиненных)"""
    if request.user.is_authenticated:
        # Если уже вошёл — сразу на дашборд
        return dashboard(request)
    return render(request, 'game/home.html')

@login_required
def dashboard(request):
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
            'percent': int(completed / total * 100) if total > 0 else 0
        }
    return render(request, 'game/dashboard.html', {'topics': topics})


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

    # Добавляем прогресс пользователя к каждому уровню
    for level in levels:
        progress, created = UserLevelProgress.objects.get_or_create(
            user=request.user,
            level=level,
            defaults={'completed': False, 'score': 0, 'attempts': 0}
        )
        level.user_progress = progress

    return render(request, 'game/topic_levels.html', {
        'topic': topic,
        'levels': levels,
    })

@login_required
def level_play(request, level_id):
    level = get_object_or_404(Level, id=level_id)
    if request.method == "POST":
        selected_option_id = request.POST.get("answer")
        if not selected_option_id:
            messages.error(request, "Выберите вариант ответа!")
            return redirect('level_play', level_id=level.id)

        selected_option = get_object_or_404(level.options, id=selected_option_id)
        is_correct = selected_option.is_correct

        progress, created = UserLevelProgress.objects.get_or_create(
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

        progress.save()

        # Перенаправляем на результат
        return redirect('level_result', level_id=level.id)

    # GET-запрос: показываем уровень
    return render(request, 'game/level_play.html', {
        'level': level,
        'options': level.options.all(),
    })


@login_required
def level_result(request, level_id):
    level = get_object_or_404(Level, id=level_id)
    progress = get_object_or_404(UserLevelProgress, user=request.user, level=level)
    correct_option = level.options.filter(is_correct=True).first()

    # Следующий уровень в теме
    next_level = Level.objects.filter(
        topic=level.topic,
        order_in_topic__gt=level.order_in_topic
    ).first()

    return render(request, 'game/level_result.html', {
        'level': level,
        'progress': progress,
        'correct_option': correct_option,
        'next_level': next_level,
    })