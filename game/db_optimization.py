"""
Функции для оптимизации запросов к БД
"""
from django.db import connection
from django.db.models import Prefetch, Count, Q
from .models import (
    Topic, Level, UserLevelProgress, 
    Achievement, UserAchievement, Notification
)


def get_optimized_topics_with_progress(user):
    """
    Оптимизированное получение тем с прогрессом пользователя
    Вместо N+1 запросов делает 2-3 запроса
    """
    # 1 запрос: все темы с уровнями
    topics = Topic.objects.prefetch_related(
        'level_set'
    ).annotate(
        total_levels=Count('level_set')
    )
    
    # 2 запрос: прогресс пользователя
    user_progress = UserLevelProgress.objects.filter(
        user=user, 
        completed=True
    ).select_related('level').values(
        'level__topic_id', 
        'level_id'
    )
    
    # Группируем прогресс по темам
    progress_map = {}
    for progress in user_progress:
        topic_id = progress['level__topic_id']
        progress_map[topic_id] = progress_map.get(topic_id, 0) + 1
    
    # Добавляем прогресс к темам
    for topic in topics:
        completed = progress_map.get(topic.id, 0)
        total = topic.total_levels
        topic.progress = {
            'percent': int(completed / total * 100) if total > 0 else 0,
            'completed': completed,
            'total': total
        }
    
    return topics


def get_optimized_levels_with_progress(user, topic):
    """
    Оптимизированное получение уровней с прогрессом
    """
    # Получаем уровни с прогрессом одним запросом
    levels = Level.objects.filter(
        topic=topic
    ).select_related(
        'topic'
    ).prefetch_related(
        Prefetch(
            'userlevelprogress_set',
            queryset=UserLevelProgress.objects.filter(user=user),
            to_attr='user_progress_list'
        )
    ).order_by('order_in_topic')
    
    # Добавляем атрибут user_progress к каждому уровню
    for level in levels:
        if level.user_progress_list:
            level.user_progress = level.user_progress_list[0]
        else:
            level.user_progress = None
    
    return levels


def get_optimized_leaderboard(limit=10):
    """
    Оптимизированное получение лидерборда
    """
    from accounts.models import User
    
    return User.objects.select_related(
        # Если есть связанные модели профиля
    ).annotate(
        total_score=Count('userlevelprogress', filter=Q(userlevelprogress__completed=True))
    ).order_by('-level', '-experience')[:limit]


def get_optimized_notifications(user, unread_only=False):
    """
    Оптимизированное получение уведомлений
    """
    query = Notification.objects.select_related('user')
    
    if unread_only:
        query = query.filter(user=user, is_read=False)
    else:
        query = query.filter(user=user)
    
    return query.order_by('-created_at')


def get_optimized_achievements_with_user_status(user):
    """
    Оптимизированное получение достижений со статусом пользователя
    """
    # Получаем все достижения
    achievements = Achievement.objects.all()
    
    # Получаем полученные достижения пользователя
    user_achievements = set(
        UserAchievement.objects.filter(
            user=user
        ).values_list('achievement_id', flat=True)
    )
    
    # Добавляем статус к каждому достижению
    for achievement in achievements:
        achievement.is_earned = achievement.id in user_achievements
    
    return achievements


def bulk_create_user_progress(user, levels):
    """
    Массовое создание прогресса для уровней
    """
    progress_objects = [
        UserLevelProgress(
            user=user,
            level=level,
            completed=False,
            score=0,
            attempts=0
        )
        for level in levels
    ]
    
    UserLevelProgress.objects.bulk_create(
        progress_objects,
        ignore_conflicts=True  # Пропускаем, если уже существует
    )


def print_query_count():
    """
    Выводит количество запросов к БД (для отладки)
    Использование:
        from game.db_optimization import print_query_count
        print_query_count()
    """
    print(f"Количество запросов к БД: {len(connection.queries)}")
    for i, query in enumerate(connection.queries, 1):
        print(f"\nЗапрос {i}:")
        print(f"SQL: {query['sql']}")
        print(f"Время: {query['time']}s")


def reset_query_count():
    """Сбрасывает счетчик запросов (для отладки)"""
    from django.db import reset_queries
    reset_queries()


# Декоратор для подсчета запросов к БД
def count_queries(func):
    """
    Декоратор для подсчета количества запросов к БД
    
    Использование:
        @count_queries
        def my_view(request):
            ...
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        reset_query_count()
        result = func(*args, **kwargs)
        query_count = len(connection.queries)
        
        if query_count > 10:
            print(f"⚠️ ВНИМАНИЕ: {func.__name__} сделал {query_count} запросов к БД!")
        else:
            print(f"✅ {func.__name__}: {query_count} запросов к БД")
        
        return result
    
    return wrapper

