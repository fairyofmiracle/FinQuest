from .models import Notification, Achievement, UserAchievement

def notifications_context(request):
    """Добавляет количество непрочитанных уведомлений в контекст всех шаблонов"""
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
        }
    return {'unread_notifications_count': 0}

def mobile_view_context(request):
    """Добавляет информацию о мобильной версии в контекст всех шаблонов"""
    return {
        'mobile_view': request.session.get('mobile_view', False)
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