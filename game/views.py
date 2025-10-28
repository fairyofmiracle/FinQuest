from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta  # ← добавлен timedelta
import json
from .models import (
    Topic, Level, UserLevelProgress, Article, Streak,
    Achievement, UserAchievement, Hint, Notification, Leaderboard,
    DailyQuest, UserDailyProgress  # ← добавлены модели ежедневных заданий
)
from accounts.models import User  # ← добавлен импорт User

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # ← редирект
    return render(request, 'game/home.html')

@login_required
def category_detail(request, category_slug):
    """Детальная страница категории с подкатегориями"""
    user = request.user
    
    # Получаем основную категорию из базы данных
    try:
        category = Topic.objects.get(main_category=category_slug, is_subcategory=False)
    except Topic.DoesNotExist:
        messages.error(request, 'Категория не найдена')
        return redirect('dashboard')
    
    # Получаем подкатегории для данной категории
    topics = Topic.objects.filter(parent_category=category, is_subcategory=True).prefetch_related('level_set')
    
    # Получаем прогресс пользователя
    user_progress = UserLevelProgress.objects.filter(user=user, completed=True).values_list('level__topic_id', flat=True)
    progress_counts = {}
    for topic_id in user_progress:
        progress_counts[topic_id] = progress_counts.get(topic_id, 0) + 1
    
    for topic in topics:
        total = topic.level_set.count()
        completed = progress_counts.get(topic.id, 0)
        topic.progress = {
            'percent': int(completed / total * 100) if total > 0 else 0,
            'completed': completed,
            'total': total
        }
    
    # Добавляем иконки для подкатегорий
    topic_icons = {
        'Бюджетирование': 'fa-calculator',
        'Сбережения': 'fa-piggy-bank',
        'Кредиты и займы': 'fa-credit-card',
        'Банковские услуги': 'fa-university',
        'Финансовое мошенничество': 'fa-exclamation-triangle',
        'Страхование': 'fa-shield',
        'Финансовая грамотность': 'fa-graduation-cap',
        'Цифровая безопасность': 'fa-lock',
        'Основы инвестирования': 'fa-chart-line',
        'Фондовый рынок': 'fa-chart-area',
        'Пассивные инвестиции': 'fa-layer-group',
        'Альтернативные инвестиции': 'fa-coins',
        'Финансовые цели': 'fa-bullseye',
        'Пенсионное планирование': 'fa-umbrella',
        'Налоговое планирование': 'fa-file-invoice',
        'Наследственное планирование': 'fa-hand-holding-heart'
    }
    
    for topic in topics:
        topic.icon = topic_icons.get(topic.name, 'fa-book')
    
    context = {
        'category': category,
        'topics': topics,
        'user': user
    }
    
    return render(request, 'game/category_detail.html', context)

def dashboard(request):
    # Если пользователь не авторизован, показываем landing page
    if not request.user.is_authenticated:
        return render(request, 'game/landing.html')
    
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
    # Пользователь считается новым, если у него нет ЗАВЕРШЕННЫХ уровней
    # (не просто started, а completed)
    has_completed_levels = UserLevelProgress.objects.filter(user=user, completed=True).exists()
    is_first_visit = not has_completed_levels
    
    # Добавляем данные о прогрессе пользователя
    user.level_progress = user.get_level_progress()
    user.achievements_count = user.get_achievements_count()
    
    # Обновляем рейтинг пользователя
    update_leaderboard(user)
    
    # Добавляем количество непрочитанных уведомлений к пользователю
    user.unread_notifications_count = unread_notifications
    
    # Группируем темы по категориям и считаем прогресс
    categories = {
        'basics': {'name': 'Основы финансов', 'icon': 'fa-piggy-bank', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
        'security': {'name': 'Безопасность', 'icon': 'fa-shield-halved', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
        'investments': {'name': 'Инвестиции', 'icon': 'fa-chart-line', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
        'planning': {'name': 'Планирование', 'icon': 'fa-bullseye', 'topics': [], 'total_levels': 0, 'completed_levels': 0},
    }
    
    for topic in topics:
        if topic.main_category in categories:
            categories[topic.main_category]['topics'].append(topic)
            categories[topic.main_category]['total_levels'] += topic.level_set.count()
            categories[topic.main_category]['completed_levels'] += progress_counts.get(topic.id, 0)
    
    # Вычисляем процент прогресса для каждой категории
    for category in categories.values():
        if category['total_levels'] > 0:
            category['progress_percent'] = int(category['completed_levels'] / category['total_levels'] * 100)
        else:
            category['progress_percent'] = 0
    
    return render(request, 'game/dashboard.html', {
        'topics': topics, 
        'categories': categories,
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
    
    # Получаем связанные статьи (из той же темы, но не текущую)
    related_articles = Article.objects.filter(
        topic=article.topic
    ).exclude(pk=pk).order_by('?')[:4]  # Случайный порядок, максимум 4
    
    return render(request, 'game/article_detail.html', {
        'article': article,
        'related_articles': related_articles
    })

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
            # Новая логика для квизов с JSON контентом
            if level.content and 'questions' in level.content:
                # Обрабатываем новый формат викторин
                question_index = int(request.POST.get('question_index', 0))
                
                if question_index < len(level.content['questions']):
                    question = level.content['questions'][question_index]
                    
                    # Проверяем тип вопроса и обрабатываем соответственно
                    question_type = question.get('type')
                    
                    if question_type == 'matching':
                        # Для сопоставления
                        selected_matches = []
                        for key in request.POST.keys():
                            if key.startswith('match_'):
                                right_idx = int(key.split('_')[1])
                                left_idx = int(request.POST.get(key))
                                selected_matches.append([left_idx, right_idx])
                        
                        correct_matches = question.get('correct_matches', [])
                        is_correct = sorted(selected_matches) == sorted(correct_matches)
                        percentage = 100 if is_correct else 0
                        user_answer = f"Сопоставлений: {len(selected_matches)}"
                        
                    elif question_type == 'sorting':
                        # Для сортировки
                        selected_order = []
                        # Собираем в правильном порядке (sort_0, sort_1, sort_2, ...)
                        sort_keys = sorted([key for key in request.POST.keys() if key.startswith('sort_')])
                        for key in sort_keys:
                            selected_order.append(int(request.POST.get(key)))
                        
                        correct_order = question.get('correct_order', [])
                        is_correct = selected_order == correct_order
                        percentage = 100 if is_correct else 0
                        user_answer = f"Порядок: {selected_order}"
                        
                    elif question.get('type') == 'multiple':
                        # Множественный выбор
                        selected_indices = request.POST.getlist('answers')
                        if not selected_indices:
                            messages.error(request, "Выберите хотя бы один вариант ответа!")
                            return redirect('level_play', level_id=level.id)
                        
                        # Проверяем правильность ответов
                        correct_indices = [i for i, option in enumerate(question['options']) if option['correct']]
                        selected_indices = [int(i) for i in selected_indices]
                        
                        # Считаем правильные и неправильные ответы
                        correct_selected = len([i for i in selected_indices if i in correct_indices])
                        incorrect_selected = len([i for i in selected_indices if i not in correct_indices])
                        missed_correct = len([i for i in correct_indices if i not in selected_indices])
                        
                        # Рассчитываем процент правильности
                        # Формула: процент правильных выбранных / общее количество правильных * 100
                        total_correct = len(correct_indices)
                        total_options = len(question['options'])
                        
                        if total_correct > 0:
                            # Процент рассчитывается как доля правильных ответов от общего числа правильных
                            percentage = max(0, min(100, (correct_selected / total_correct) * 100))
                        else:
                            percentage = 0
                        
                        is_correct = percentage >= 80
                        user_answer = f"Выбрано: {len(selected_indices)} из {len(question['options'])} вариантов"
                        
                    else:
                        # Одиночный выбор
                        selected_option_index = int(request.POST.get('answer', -1))
                        if selected_option_index < 0:
                            messages.error(request, "Выберите вариант ответа!")
                            return redirect('level_play', level_id=level.id)
                        
                        if 0 <= selected_option_index < len(question['options']):
                            selected_option = question['options'][selected_option_index]
                            is_correct = selected_option['correct']
                            user_answer = selected_option['text']
                            percentage = 100 if is_correct else 0
                        else:
                            messages.error(request, "Неверный вариант ответа!")
                            return redirect('level_play', level_id=level.id)
                        
                    # Сохраняем ответ в сессии для накопления результатов
                    session_key = f"quiz_answers_{level.id}"
                    if session_key not in request.session:
                        request.session[session_key] = []
                    
                    # Получаем текст вопроса для сохранения
                    question_text = level.content['questions'][question_index]['question']
                    
                    # Сохраняем в сессию в зависимости от типа вопроса
                    if question.get('type') == 'matching':
                        # Для matching сохраняем сопоставления
                        request.session[session_key].append({
                            'question_index': question_index,
                            'matches': selected_matches,
                            'correct': is_correct,
                            'text': user_answer,
                            'question_text': question_text,
                            'type': 'matching',
                            'percentage': percentage
                        })
                    elif question.get('type') == 'sorting':
                        # Для sorting сохраняем порядок
                        request.session[session_key].append({
                            'question_index': question_index,
                            'order': selected_order,
                            'correct': is_correct,
                            'text': user_answer,
                            'question_text': question_text,
                            'type': 'sorting',
                            'percentage': percentage
                        })
                    elif question.get('type') == 'multiple':
                        # Для множественного выбора сохраняем все выбранные индексы
                        request.session[session_key].append({
                            'question_index': question_index,
                            'answers': selected_indices,
                            'correct': is_correct,
                            'text': user_answer,
                            'question_text': question_text,
                            'type': 'multiple',
                            'percentage': percentage
                        })
                    else:
                        # Для одиночного выбора
                        request.session[session_key].append({
                            'question_index': question_index,
                            'answer': selected_option_index,
                            'correct': is_correct,
                            'text': user_answer,
                            'question_text': question_text,
                            'type': 'single',
                            'percentage': percentage
                        })
                    
                    # Сохраняем изменения в сессии
                    request.session.modified = True
                    
                    # Проверяем, все ли вопросы отвечены
                    current_answered = len(request.session[session_key])
                    total_questions = len(level.content['questions'])
                    
                    if current_answered < total_questions:
                        # Есть еще вопросы, перенаправляем на следующий
                        if is_correct:
                            messages.success(request, f"Правильно! Переходим к вопросу {current_answered + 1}")
                        else:
                            messages.warning(request, f"Неправильно! Переходим к вопросу {current_answered + 1}")
                        return redirect('level_play', level_id=level.id)
                    else:
                        # Все вопросы отвечены, завершаем викторину
                        answers = request.session.get(session_key, [])
                        
                        # Подсчитываем результаты с учетом типа вопросов
                        total_score = 0
                        total_questions = len(level.content['questions'])
                        
                        for answer in answers:
                            answer_percentage = answer.get('percentage', 0)
                            total_score += answer_percentage
                        
                        # Рассчитываем общий процент ПОСЛЕ цикла
                        percentage = int(total_score / total_questions) if total_questions > 0 else 0
                        is_correct = percentage >= 80  # 80% и выше считается успешным
                        user_answer = f"Общий результат: {percentage}%"
                        
                        # Очищаем сессию
                        if session_key in request.session:
                            del request.session[session_key]
                        
                        # Сохраняем детальную информацию о результатах для отображения
                        quiz_results = {
                            'total_questions': total_questions,
                            'percentage': percentage,
                            'is_correct': is_correct,
                            'answers': answers,  # Детальная информация о каждом ответе
                            'questions': level.content['questions']  # Вопросы для отображения
                        }
                        
                        # Переходим к обработке результата
                        progress = UserLevelProgress.objects.get(
                            user=request.user,
                            level=level
                        )
                        progress.attempts += 1

                        if is_correct and not progress.completed:
                            old_points = request.user.points
                            old_coins = request.user.coins
                            old_level = request.user.level_number  # Сохраняем старый уровень
                            
                            request.user.points += level.reward_points
                            request.user.coins += level.reward_coins
                            new_level = request.user.get_level_number()
                            request.user.level_number = new_level
                            request.user.save()
                            
                            # Проверяем повышение уровня
                            if new_level > old_level:
                                # Определяем новую рамку аватара на основе уровня
                                new_border = 'novice'
                                if new_level >= 7: new_border = 'legend'
                                elif new_level >= 6: new_border = 'master'
                                elif new_level >= 5: new_border = 'expert'
                                elif new_level >= 4: new_border = 'advanced'
                                elif new_level >= 3: new_border = 'intermediate'
                                elif new_level >= 2: new_border = 'beginner'
                                
                                request.session['level_up'] = {
                                    'old_level': old_level,
                                    'new_level': new_level,
                                    'level_title': request.user.get_level_title(),
                                    'new_border_class': f'avatar-border-{new_border}'
                                }
                                request.session.modified = True
                            
                            progress.completed = True
                            progress.score = percentage
                            
                            # Сохраняем время прохождения
                            completion_time = int(request.POST.get('completion_time', 0))
                            if completion_time > 0:
                                progress.completion_time = completion_time
                                if progress.best_time == 0 or completion_time < progress.best_time:
                                    progress.best_time = completion_time
                            
                            # Обновляем прогресс ежедневных заданий
                            update_daily_quest_progress(request.user, 'levels_completed', 1)
                            update_daily_quest_progress(request.user, 'points_earned', level.reward_points)
                            
                            # Создаем уведомления о получении наград
                            if getattr(request.user, 'notifications_enabled', True):
                                if level.reward_points > 0:
                                    Notification.objects.create(
                                        user=request.user,
                                        text=f"Получено {level.reward_points} очков за прохождение уровня!"
                                    )
                                if level.reward_coins > 0:
                                    Notification.objects.create(
                                        user=request.user,
                                        text=f"Получено {level.reward_coins} монет за прохождение уровня!"
                                    )
                        else:
                            progress.score = percentage
                        
                        # Обновляем лучшую попытку
                        if progress.score is not None:
                            progress.best_score = max(progress.best_score or 0, progress.score)
                        
                        progress.save()
                        
                        # Сохраняем результаты викторины в сессии для отображения
                        request.session[f'quiz_results_{level.id}'] = quiz_results
                        request.session.modified = True
                        
                        return redirect('level_result', level_id=level.id)
                else:
                    messages.error(request, "Ошибка в данных вопроса!")
                    return redirect('level_play', level_id=level.id)
            else:
                # Старая логика для квизов с LevelOption
                selected_option_id = request.POST.get("answer")
                if not selected_option_id:
                    messages.error(request, "Выберите вариант ответа!")
                    return redirect('level_play', level_id=level.id)
                selected_option = get_object_or_404(level.options, id=selected_option_id)
                is_correct = selected_option.is_correct
                user_answer = selected_option.text
            
        elif level.type in ['test', 'quest', 'story', 'puzzle', 'scenario', 'calculation', 'matching', 'sorting', 'simulation']:
            # Новая логика для других типов уровней
            result = process_level_answer(level, request.POST)
            
            # Обработка специального случая для квестов
            if result == 'continue':
                # Квест продолжается, не завершаем уровень
                messages.info(request, "Правильно! Переходим к следующему шагу.")
                return redirect('level_play', level_id=level.id)
            
            is_correct, user_answer = result

        # Обрабатываем результат только для не-викторин
        if level.type != 'quiz' or not (level.content and 'questions' in level.content):
            # Получаем существующий прогресс (он уже создан в GET запросе)
            progress = UserLevelProgress.objects.get(
                user=request.user,
                level=level
            )
            progress.attempts += 1

            # Для не-викторин используем систему 80%
            score = 100 if is_correct else 0
            is_successful = score >= 80

            if is_successful and not progress.completed:
                old_points = request.user.points
                old_coins = request.user.coins
                old_level = request.user.level_number  # Сохраняем старый уровень
                
                request.user.points += level.reward_points
                request.user.coins += level.reward_coins
                new_level = request.user.get_level_number()
                request.user.level_number = new_level
                request.user.save()
                
                # Проверяем повышение уровня
                if new_level > old_level:
                    # Определяем новую рамку аватара на основе уровня
                    new_border = 'novice'
                    if new_level >= 7: new_border = 'legend'
                    elif new_level >= 6: new_border = 'master'
                    elif new_level >= 5: new_border = 'expert'
                    elif new_level >= 4: new_border = 'advanced'
                    elif new_level >= 3: new_border = 'intermediate'
                    elif new_level >= 2: new_border = 'beginner'
                    
                    request.session['level_up'] = {
                        'old_level': old_level,
                        'new_level': new_level,
                        'level_title': request.user.get_level_title(),
                        'new_border_class': f'avatar-border-{new_border}'
                    }
                    request.session.modified = True
                progress.completed = True
                progress.score = score
                
                # Сохраняем время прохождения
                completion_time = int(request.POST.get('completion_time', 0))
                if completion_time > 0:
                    progress.completion_time = completion_time
                    if progress.best_time == 0 or completion_time < progress.best_time:
                        progress.best_time = completion_time
                
                # Обновляем прогресс ежедневных заданий
                update_daily_quest_progress(request.user, 'levels_completed', 1)
                update_daily_quest_progress(request.user, 'points_earned', level.reward_points)
                
                # Создаем уведомления о получении наград
                if getattr(request.user, 'notifications_enabled', True):
                    if level.reward_points > 0:
                        Notification.objects.create(
                            user=request.user,
                            text=f"Получено {level.reward_points} очков за прохождение уровня!"
                        )
                    if level.reward_coins > 0:
                        Notification.objects.create(
                            user=request.user,
                            text=f"Получено {level.reward_coins} монет за прохождение уровня!"
                        )
            else:
                progress.score = score

            # Обновляем лучшую попытку
            if progress.score is not None:
                progress.best_score = max(progress.best_score or 0, progress.score)

            progress.save()
            return redirect('level_result', level_id=level.id)

    # Определяем, какой шаблон использовать
    template_name = 'game/level_play_improved.html'
    
    # Создаем или получаем прогресс пользователя для этого уровня
    progress, created = UserLevelProgress.objects.get_or_create(
        user=request.user,
        level=level,
        defaults={'attempts': 0, 'completed': False, 'score': 0, 'best_score': 0}
    )
    
    # Подготавливаем данные для викторины
    quiz_data = None
    if level.type == 'quiz' and level.content and 'questions' in level.content:
        # Определяем текущий вопрос на основе сессии
        session_key = f"quiz_answers_{level.id}"
        answered_questions = len(request.session.get(session_key, []))
        total_questions = len(level.content['questions'])
        
        # Определяем текущий вопрос для отображения
        if answered_questions >= total_questions:
            # Все вопросы отвечены, перенаправляем на результат
            return redirect('level_result', level_id=level.id)
        else:
            # Показываем следующий неотвеченный вопрос
            current_question = answered_questions
        
        # Получаем текущий вопрос для отображения
        current_question_data = level.content['questions'][current_question] if current_question < len(level.content['questions']) else None
        
        quiz_data = {
            'questions': level.content['questions'],
            'current_question': current_question,
            'current_question_data': current_question_data,
            'total_questions': len(level.content['questions']),
            'answered_questions': answered_questions,
            'current_question_number': current_question + 1  # Номер вопроса для отображения (1-based)
        }
    
    # Проверяем, была ли использована подсказка для викторины
    hint_used = False
    if level.type == 'quiz' and level.content and 'questions' in level.content:
        hint_session_key = f"hint_used_{level.id}"
        hint_used = bool(request.session.get(hint_session_key))
    
    return render(request, template_name, {
        'level': level,
        'options': level.options.all(),
        'quiz_data': quiz_data,
        'hint': hint,
        'hint_shown': hint_used,
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
    
    # Проверяем повышение уровня
    level_up_data = request.session.pop('level_up', None)
    if level_up_data:
        # Передаем данные в контекст
        pass
    else:
        level_up_data = None

    # Получаем результаты викторины из сессии
    quiz_results = request.session.get(f'quiz_results_{level_id}', None)
    
    # Очищаем результаты из сессии после получения
    if f'quiz_results_{level_id}' in request.session:
        del request.session[f'quiz_results_{level_id}']

    # 🔥 Вызываем систему серий и достижений
    update_streak(request.user)
    new_achievements = check_achievements(request.user)

    return render(request, 'game/level_result.html', {
        'level': level,
        'progress': progress,
        'correct_option': correct_option,
        'next_level': next_level,
        'quiz_results': quiz_results,
        'new_achievements': json.dumps(new_achievements),
        'level_up_data': level_up_data,
        'level_up_data_json': json.dumps(level_up_data) if level_up_data else 'null',
    })

# --- Вспомогательные функции ---

def check_achievements(user):
    new_achievements = []
    
    # Проверяем достижение "Первые шаги" - первый ответ
    if not UserAchievement.objects.filter(user=user, achievement__name="Первые шаги").exists():
        first_answer_achievement = Achievement.objects.filter(name="Первые шаги").first()
        if first_answer_achievement:
            # Проверяем, есть ли у пользователя хотя бы один ответ
            has_answered = UserLevelProgress.objects.filter(user=user).exists()
            if has_answered:
                UserAchievement.objects.create(user=user, achievement=first_answer_achievement)
                new_achievements.append({
                    'name': first_answer_achievement.name,
                    'description': first_answer_achievement.description,
                    'icon': first_answer_achievement.icon
                })
                
                if getattr(user, 'notifications_enabled', True):
                    Notification.objects.create(
                        user=user,
                        text=f"🏆 Получено достижение: {first_answer_achievement.name}"
                    )
    
    # Достижения по темам
    for topic in Topic.objects.all():
        total = topic.level_set.count()
        completed = UserLevelProgress.objects.filter(
            user=user, level__topic=topic, completed=True
        ).count()
        if total > 0 and completed == total:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"Мастер {topic.name}",
                defaults={
                    "description": f"Пройдены все уровни по теме «{topic.name}»",
                    "icon": "fa-trophy",
                    "rarity": "common"
                }
            )
            ua, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created:
                # Обновляем прогресс ежедневных заданий
                update_daily_quest_progress(user, 'achievements_earned', 1)
                
                if getattr(user, 'notifications_enabled', True):
                    Notification.objects.create(
                        user=user,
                        text=f"🏆 Получено достижение: {achievement.name}"
                    )
                
                # Добавляем в список новых достижений
                new_achievements.append({
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'rarity': achievement.rarity,
                    'rarity_display': achievement.get_rarity_display()
                })
    
    # Достижения по общему прогрессу
    total_levels_completed = UserLevelProgress.objects.filter(user=user, completed=True).count()
    total_achievements = UserAchievement.objects.filter(user=user).count()
    total_points = user.points
    
    # Достижения за количество пройденных уровней
    level_milestones = [10, 25, 50, 100]
    for milestone in level_milestones:
        if total_levels_completed >= milestone:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"Исследователь {milestone}",
                defaults={"description": f"Пройдено {milestone} уровней"}
            )
            ua, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created and getattr(user, 'notifications_enabled', True):
                Notification.objects.create(
                    user=user,
                    text=f"🎯 Получено достижение: {achievement.name}"
                )
    
    # Достижения за очки
    points_milestones = [500, 1000, 2500, 5000]
    for milestone in points_milestones:
        if total_points >= milestone:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"Богач {milestone}",
                defaults={"description": f"Заработано {milestone} очков"}
            )
            ua, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created and getattr(user, 'notifications_enabled', True):
                Notification.objects.create(
                    user=user,
                    text=f"💰 Получено достижение: {achievement.name}"
                )
    
    # Достижения за серии
    try:
        streak = Streak.objects.get(user=user)
        streak_milestones = [7, 14, 30, 100]
        for milestone in streak_milestones:
            if streak.current_streak >= milestone:
                achievement, _ = Achievement.objects.get_or_create(
                    name=f"Постоянство {milestone}",
                    defaults={"description": f"Серия в {milestone} дней"}
                )
                ua, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
                if created and getattr(user, 'notifications_enabled', True):
                    Notification.objects.create(
                        user=user,
                        text=f"🔥 Получено достижение: {achievement.name}"
                    )
    except Streak.DoesNotExist:
        pass
    
    # Достижения за достижения
    achievement_milestones = [5, 10, 20, 50]
    for milestone in achievement_milestones:
        if total_achievements >= milestone:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"Коллекционер {milestone}",
                defaults={"description": f"Получено {milestone} достижений"}
            )
            ua, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
            if created:
                # Обновляем прогресс ежедневных заданий
                update_daily_quest_progress(user, 'achievements_earned', 1)
                
                if getattr(user, 'notifications_enabled', True):
                    Notification.objects.create(
                        user=user,
                        text=f"🏆 Получено достижение: {achievement.name}"
                    )
                
    # Проверяем повышение уровня
    old_level = user.level_number
    new_level = user.get_level_number()
    if new_level > old_level:
        user.level_number = new_level
        user.save()
        if getattr(user, 'notifications_enabled', True):
            Notification.objects.create(
                user=user,
                text=f"🎉 Поздравляем! Вы достигли {user.get_level_title()} (уровень {new_level})!"
            )
    
    return new_achievements

def update_streak(user):
    streak, _ = Streak.objects.get_or_create(user=user)
    today = date.today()
    if streak.last_activity == today:
        return
    elif streak.last_activity == today - timedelta(days=1):
        streak.current_streak += 1
        
        # Уведомления о достижении определенных серий
        if getattr(user, 'notifications_enabled', True):
            if streak.current_streak == 3:
                Notification.objects.create(
                    user=user,
                    text="🔥 Отличная серия! 3 дня подряд!"
                )
            elif streak.current_streak == 7:
                Notification.objects.create(
                    user=user,
                    text="🏆 Невероятно! 7 дней подряд!"
                )
            elif streak.current_streak == 14:
                Notification.objects.create(
                    user=user,
                    text="💎 Легендарная серия! 14 дней подряд!"
                )
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
    # Если content - строка (JSON), парсим её
    if isinstance(content, str):
        import json
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {}
    
    if level.type == 'quiz':
        # Викторина с множественными вопросами
        questions = level.options.values_list('question_number', flat=True).distinct()
        total_questions = len(questions)
        correct_answers = 0
        
        for question_num in questions:
            selected_option_id = post_data.get(f'answer_{question_num}')
            if selected_option_id:
                selected_option = level.options.get(id=selected_option_id)
                if selected_option.is_correct:
                    correct_answers += 1
        
        if total_questions == 0:
            return False, "Нет вопросов"
        
        is_correct = correct_answers == total_questions
        return is_correct, f"Правильных ответов: {correct_answers} из {total_questions}"
    
    elif level.type == 'test':
        # Тест с множественными вопросами и несколькими правильными ответами
        questions = level.options.values_list('question_number', flat=True).distinct()
        total_questions = len(questions)
        correct_answers = 0
        
        for question_num in questions:
            selected_options = post_data.getlist(f'answer_{question_num}')
            if selected_options:
                correct_options = level.options.filter(question_number=question_num, is_correct=True)
                correct_ids = [str(opt.id) for opt in correct_options]
                
                # Проверяем, что выбраны только правильные ответы и все правильные выбраны
                if set(selected_options) == set(correct_ids):
                    correct_answers += 1
        
        if total_questions == 0:
            return False, "Нет вопросов"
        
        is_correct = correct_answers == total_questions
        return is_correct, f"Правильных ответов: {correct_answers} из {total_questions}"
    
    elif level.type == 'quest':
        # Интерактивный квест с последовательными шагами
        step = int(post_data.get('current_step', 1))
        answer = post_data.get('quest_answer', '')
        
        # Получаем данные шага
        steps_data = content.get('steps', {})
        current_step_data = steps_data.get(str(step), {})
        correct_answers = current_step_data.get('correct_answers', [])
        total_steps = content.get('total_steps', 1)
        
        is_correct = answer.lower().strip() in [ans.lower().strip() for ans in correct_answers]
        
        if is_correct and step < total_steps:
            return 'continue', f"Шаг {step} пройден, продолжаем..."
        elif is_correct:
            return True, f"Квест завершен! Все шаги пройдены."
        else:
            return False, f"Неверный ответ на шаге {step}"
    
    elif level.type == 'story':
        # История с выбором - игрок делает выборы, влияющие на исход
        choice_id = post_data.get('story_choice')
        if not choice_id:
            return False, "Выбор не сделан"
        
        choices = content.get('choices', {})
        choice = choices.get(choice_id, {})
        is_correct = choice.get('is_correct', False)
        consequence = choice.get('consequence', '')
        
        return is_correct, f"Последствие: {consequence}"
    
    elif level.type == 'puzzle':
        # Головоломка - нужно разгадать загадку или решить задачу
        user_answer = post_data.get('puzzle_answer', '').lower().strip()
        correct_answers = content.get('correct_answers', [])
        is_correct = user_answer in [ans.lower().strip() for ans in correct_answers]
        
        return is_correct, f"Ваш ответ: {post_data.get('puzzle_answer', '')}"
    
    elif level.type == 'scenario':
        # Обработка сценариев
        try:
            selected_option_str = post_data.get('scenario_answer', '0')
            selected_option = int(selected_option_str) if selected_option_str else 0
        except (ValueError, TypeError):
            selected_option = 0
            
        correct_answer = content.get('correct_answer', 0)
        return selected_option == correct_answer, f"Выбрано: {selected_option + 1}"
    
    elif level.type == 'calculation':
        # Расчеты с множественными задачами
        questions = content.get('questions', [])
        total_questions = len(questions)
        correct_answers = 0
        
        for i, question_data in enumerate(questions, 1):
            try:
                user_answer_str = post_data.get(f'calculation_answer_{i}', '0')
                user_answer = float(user_answer_str) if user_answer_str else 0
            except (ValueError, TypeError):
                user_answer = 0
                
            correct_answer = question_data.get('correct_answer', 0)
            tolerance = question_data.get('tolerance', 0)
            if abs(user_answer - correct_answer) <= tolerance:
                correct_answers += 1
        
        if total_questions == 0:
            return False, "Нет задач"
        
        is_correct = correct_answers == total_questions
        return is_correct, f"Правильных ответов: {correct_answers} из {total_questions}"
    
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
        try:
            response_index_str = post_data.get('simulation_response', '0')
            response_index = int(response_index_str) if response_index_str else 0
        except (ValueError, TypeError):
            response_index = 0
            
        dialogue = content.get('dialogue', [])
        if dialogue and len(dialogue) > 0:
            first_dialogue = dialogue[0]
            responses = first_dialogue.get('responses', [])
            if response_index < len(responses):
                response = responses[response_index]
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


def update_daily_quest_progress(user, quest_type, progress_value=1):
    """Обновляет прогресс по ежедневным заданиям"""
    today = date.today()
    active_quests = DailyQuest.objects.filter(
        quest_type=quest_type, 
        is_active=True
    )
    
    for quest in active_quests:
        user_progress, created = UserDailyProgress.objects.get_or_create(
            user=user,
            quest=quest,
            date=today,
            defaults={'current_progress': 0}
        )
        
        if not user_progress.completed_at:  # Если задание еще не выполнено
            user_progress.current_progress += progress_value
            user_progress.save()
            
            # Проверяем, выполнено ли задание
            if user_progress.current_progress >= quest.target_value:
                user_progress.completed_at = date.today()
                user_progress.save()
                
                # Выдаем награды
                user.coins += quest.reward_coins
                user.points += quest.reward_points
                user.level_number = user.get_level_number()  # Обновляем уровень
                user.save()
                
                # Создаем уведомление
                if getattr(user, 'notifications_enabled', True):
                    Notification.objects.create(
                        user=user,
                        text=f"🎁 Задание выполнено! Получено {quest.reward_coins} монет и {quest.reward_points} очков!"
                    )


def get_daily_quests_for_user(user):
    """Возвращает ежедневные задания с прогрессом пользователя"""
    today = date.today()
    quests = DailyQuest.objects.filter(is_active=True)
    
    user_quests = []
    for quest in quests:
        try:
            user_progress = UserDailyProgress.objects.get(
                user=user,
                quest=quest,
                date=today
            )
            progress_percent = int((user_progress.current_progress / quest.target_value) * 100)
            is_completed = user_progress.completed_at is not None
        except UserDailyProgress.DoesNotExist:
            user_progress = None
            progress_percent = 0
            is_completed = False
        
        user_quests.append({
            'quest': quest,
            'progress': user_progress,
            'progress_percent': progress_percent,
            'is_completed': is_completed
        })
    
    return user_quests

@login_required
def notifications_list(request):
    from django.core.paginator import Paginator
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            messages.success(request, "Уведомления отмечены как прочитанные")
            return redirect('notifications_list')
        elif action == 'delete_all':
            Notification.objects.filter(user=request.user).delete()
            messages.success(request, "Все уведомления удалены")
            return redirect('notifications_list')
    
    # Пагинация - по 10 уведомлений на страницу
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'game/notifications.html', {'notifications': page_obj})

@login_required
def daily_quests(request):
    """Ежедневные задания"""
    user_quests = get_daily_quests_for_user(request.user)
    
    return render(request, 'game/daily_quests.html', {
        'user_quests': user_quests,
    })


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


