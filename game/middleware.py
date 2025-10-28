"""
Middleware для безопасности и производительности
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import time


class RateLimitMiddleware:
    """
    Middleware для ограничения частоты запросов (rate limiting)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем rate limit для чувствительных операций
        if request.path in ['/accounts/login/', '/accounts/register/']:
            ip = self.get_client_ip(request)
            cache_key = f'rate_limit_{request.path}_{ip}'
            
            # Получаем количество запросов за последнюю минуту
            request_count = cache.get(cache_key, 0)
            
            # Ограничение: максимум 5 попыток в минуту
            if request_count >= 5:
                return HttpResponseForbidden(
                    "Слишком много попыток. Попробуйте через минуту."
                )
            
            # Увеличиваем счетчик
            cache.set(cache_key, request_count + 1, 60)  # TTL 60 секунд
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Получает реальный IP клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Middleware для добавления заголовков безопасности
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Защита от XSS
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy (базовый)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
        )
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


@receiver(user_login_failed)
def handle_failed_login(sender, credentials, request, **kwargs):
    """
    Обработчик неудачных попыток входа
    """
    ip = RateLimitMiddleware.get_client_ip(request)
    username = credentials.get('username', 'unknown')
    
    # Логируем неудачную попытку
    cache_key = f'failed_login_{ip}_{username}'
    failed_attempts = cache.get(cache_key, 0)
    cache.set(cache_key, failed_attempts + 1, 3600)  # Храним час
    
    # Если слишком много неудачных попыток, блокируем на 15 минут
    if failed_attempts >= 10:
        block_key = f'blocked_{ip}_{username}'
        cache.set(block_key, True, 900)  # 15 минут

