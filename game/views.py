from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Level, UserLevelProgress

def home(request):
    """Главная страница для всех (анонимных и залогиненных)"""
    if request.user.is_authenticated:
        # Если уже вошёл — сразу на дашборд
        return dashboard(request)
    return render(request, 'game/home.html')

@login_required
def dashboard(request):
    """Дашборд с темами — только для авторизованных"""
    from .models import Topic
    topics = Topic.objects.all()
    return render(request, 'game/dashboard.html', {'topics': topics})

@login_required
def topic_levels(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    levels = Level.objects.filter(topic=topic).order_by('order_in_topic')
    return render(request, 'game/topic_levels.html', {'topic': topic, 'levels': levels})

@login_required
def level_play(request, level_id):
    level = get_object_or_404(Level, id=level_id)
    options = level.options.all()

    if request.method == "POST":
        selected_option_id = request.POST.get("answer")
        selected_option = get_object_or_404(level.options, id=selected_option_id)

        progress, created = UserLevelProgress.objects.get_or_create(
            user=request.user,
            level=level,
            defaults={'attempts': 0}
        )
        progress.attempts += 1

        if selected_option.is_correct:
            if not progress.completed:  # начисляем только при первом прохождении
                request.user.points += level.reward_points
                request.user.coins += level.reward_coins
                request.user.save()
                progress.completed = True
                progress.score = 100
            else:
                progress.score = 100
        else:
            progress.score = 0

        progress.save()

        # Перенаправляем на результат (пока просто на тему)
        return redirect('topic_levels', topic_id=level.topic.id)

    return render(request, 'game/level_play.html', {
        'level': level,
        'options': options
    })