from .models import Notification, Achievement, UserAchievement

def notifications_context(request):
    """Добавляет количество непрочитанных уведомлений в контекст всех шаблонов"""
    try:
        if request.user.is_authenticated:
            return {
                'unread_notifications_count': Notification.objects.filter(
                    user=request.user, 
                    is_read=False
                ).count()
            }
    except Exception:
        # В случае ошибки возвращаем 0, чтобы не ломать шаблоны
        pass
    return {'unread_notifications_count': 0}

def mobile_view_context(request):
    """Автоматически определяет мобильное устройство по User-Agent"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    # Список ключевых слов для определения мобильных устройств
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipod', 'ipad', 
        'blackberry', 'windows phone', 'webos', 'opera mini',
        'iemobile', 'mobile safari'
    ]
    
    # Проверяем есть ли мобильные ключевые слова в User-Agent
    is_mobile = any(keyword in user_agent for keyword in mobile_keywords)
    
    # Можно переопределить через сессию (для тестирования)
    if 'force_mobile_view' in request.session:
        is_mobile = request.session['force_mobile_view']
    
    return {
        'mobile_view': is_mobile
    }

def achievements_context(request):
    """Добавляет достижения пользователя в контекст всех шаблонов (для мобильного меню)"""
    if request.user.is_authenticated:
        # Получаем только полученные достижения, ограничиваем до 10 последних
        user_achievements = UserAchievement.objects.filter(
            user=request.user
        ).select_related('achievement').order_by('-earned_at')[:10]
        
        achievements_list = []
        for ua in user_achievements:
            achievements_list.append({
                'achievement': ua.achievement,
                'earned_at': ua.earned_at
            })
        
        return {
            'mobile_achievements': achievements_list,
            'mobile_achievements_count': UserAchievement.objects.filter(user=request.user).count()
        }
    return {
        'mobile_achievements': [],
        'mobile_achievements_count': 0
    }