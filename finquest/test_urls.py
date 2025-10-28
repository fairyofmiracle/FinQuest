from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from accounts.views import custom_logout

User = get_user_model()

class URLPatternsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_url(self):
        """Тестирует URL главной страницы"""
        url = reverse('dashboard')
        self.assertEqual(url, '/')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Редирект на логин
    
    def test_dashboard_url(self):
        """Тестирует URL дашборда"""
        url = reverse('dashboard')
        self.assertEqual(url, '/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_media_url(self):
        """Тестирует URL медиа"""
        url = reverse('media')
        self.assertEqual(url, '/media/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_article_detail_url(self):
        """Тестирует URL детальной страницы статьи"""
        from game.models import Topic, Article
        
        topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        article = Article.objects.create(
            title='Тестовая статья',
            content='Содержимое статьи',
            topic=topic
        )
        
        url = reverse('article_detail', args=[article.pk])
        self.assertEqual(url, f'/media/{article.pk}/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_topic_levels_url(self):
        """Тестирует URL уровней темы"""
        from game.models import Topic
        
        topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        url = reverse('topic_levels', args=[topic.id])
        self.assertEqual(url, f'/topic/{topic.id}/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_level_play_url(self):
        """Тестирует URL прохождения уровня"""
        from game.models import Topic, Level
        
        topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        level = Level.objects.create(
            title='Тестовый уровень',
            topic=topic,
            type='quiz',
            order_in_topic=1
        )
        
        url = reverse('level_play', args=[level.id])
        self.assertEqual(url, f'/level/{level.id}/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_level_result_url(self):
        """Тестирует URL результата уровня"""
        from game.models import Topic, Level, UserLevelProgress
        
        topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        level = Level.objects.create(
            title='Тестовый уровень',
            topic=topic,
            type='quiz',
            order_in_topic=1
        )
        
        # Создаем прогресс пользователя
        UserLevelProgress.objects.create(
            user=self.user,
            level=level,
            completed=True,
            score=100
        )
        
        url = reverse('level_result', args=[level.id])
        self.assertEqual(url, f'/level/{level.id}/result/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_notifications_url(self):
        """Тестирует URL уведомлений"""
        url = reverse('notifications_list')
        self.assertEqual(url, '/notifications/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_daily_quests_url(self):
        """Тестирует URL ежедневных заданий"""
        url = reverse('daily_quests')
        self.assertEqual(url, '/daily-quests/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_leaderboard_url(self):
        """Тестирует URL рейтинга"""
        url = reverse('leaderboard')
        self.assertEqual(url, '/leaderboard/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class AccountsURLPatternsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_url(self):
        """Тестирует URL входа"""
        url = reverse('login')
        self.assertEqual(url, '/accounts/login/')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_logout_url(self):
        """Тестирует URL выхода"""
        url = reverse('logout')
        self.assertEqual(url, '/accounts/logout/')
        
        # Без авторизации должен работать (показывает страницу выхода)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_register_url(self):
        """Тестирует URL регистрации"""
        url = reverse('register')
        self.assertEqual(url, '/accounts/register/')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_profile_url(self):
        """Тестирует URL профиля"""
        url = reverse('profile')
        self.assertEqual(url, '/accounts/profile/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_settings_url(self):
        """Тестирует URL настроек"""
        url = reverse('settings')
        self.assertEqual(url, '/accounts/settings/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_reset_progress_url(self):
        """Тестирует URL сброса прогресса"""
        url = reverse('reset_progress')
        self.assertEqual(url, '/accounts/reset/')
        
        # Без авторизации должен редиректить
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # С авторизацией должен работать
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class URLResolveTest(TestCase):
    """Тестирует разрешение URL"""
    
    def test_home_url_resolves(self):
        """Тестирует разрешение URL главной страницы"""
        from game.views import dashboard
        url = reverse('dashboard')
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func, dashboard)
    
    def test_dashboard_url_resolves(self):
        """Тестирует разрешение URL дашборда"""
        from game.views import dashboard
        url = reverse('dashboard')
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func, dashboard)
    
    def test_logout_url_resolves(self):
        """Тестирует разрешение URL выхода"""
        url = reverse('logout')
        resolved_func = resolve(url).func
        self.assertEqual(resolved_func, custom_logout)
    
    def test_login_url_resolves(self):
        """Тестирует разрешение URL входа"""
        from django.contrib.auth.views import LoginView
        url = reverse('login')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, LoginView)
    
    def test_register_url_resolves(self):
        """Тестирует разрешение URL регистрации"""
        from accounts.views import RegisterView
        url = reverse('register')
        resolved_view = resolve(url).func.view_class
        self.assertEqual(resolved_view, RegisterView)

class URLParametersTest(TestCase):
    """Тестирует URL с параметрами"""
    
    def setUp(self):
        from game.models import Topic, Level, Article
        
        self.topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        self.level = Level.objects.create(
            title='Тестовый уровень',
            topic=self.topic,
            type='quiz',
            order_in_topic=1
        )
        
        self.article = Article.objects.create(
            title='Тестовая статья',
            content='Содержимое статьи',
            topic=self.topic
        )
    
    def test_topic_levels_url_with_parameters(self):
        """Тестирует URL уровней темы с параметрами"""
        url = reverse('topic_levels', args=[self.topic.id])
        expected_url = f'/topic/{self.topic.id}/'
        self.assertEqual(url, expected_url)
    
    def test_level_play_url_with_parameters(self):
        """Тестирует URL прохождения уровня с параметрами"""
        url = reverse('level_play', args=[self.level.id])
        expected_url = f'/level/{self.level.id}/'
        self.assertEqual(url, expected_url)
    
    def test_level_result_url_with_parameters(self):
        """Тестирует URL результата уровня с параметрами"""
        url = reverse('level_result', args=[self.level.id])
        expected_url = f'/level/{self.level.id}/result/'
        self.assertEqual(url, expected_url)
    
    def test_article_detail_url_with_parameters(self):
        """Тестирует URL детальной страницы статьи с параметрами"""
        url = reverse('article_detail', args=[self.article.pk])
        expected_url = f'/media/{self.article.pk}/'
        self.assertEqual(url, expected_url)

class URLRedirectTest(TestCase):
    """Тестирует редиректы URL"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_redirects_when_authenticated(self):
        """Тестирует редирект главной страницы при авторизации"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)  # Дашборд показывается напрямую
    
    def test_protected_urls_redirect_to_login(self):
        """Тестирует редирект защищенных URL на страницу входа"""
        protected_urls = [
            '/',  # Главная страница (дашборд)
            '/media/',
            '/notifications/',
            '/daily-quests/',
            '/leaderboard/',
            '/accounts/profile/',
            '/accounts/settings/',
            '/accounts/reset/',
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, f'/accounts/login/?next={url}')
    
    def test_login_redirects_after_successful_login(self):
        """Тестирует редирект после успешного входа"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
    
    def test_register_redirects_after_successful_registration(self):
        """Тестирует редирект после успешной регистрации"""
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
