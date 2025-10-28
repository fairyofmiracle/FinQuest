from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from .models import User
from .forms import CustomUserCreationForm

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')
    
    def test_user_default_values(self):
        self.assertEqual(self.user.points, 0)
        self.assertEqual(self.user.coins, 0)
        self.assertEqual(self.user.level_number, 1)
        self.assertTrue(self.user.notifications_enabled)
    
    def test_user_level_calculation(self):
        # Тестируем расчет уровня пользователя
        self.user.points = 1000
        self.user.save()
        
        level = self.user.get_level_number()
        self.assertIsInstance(level, int)
        self.assertGreater(level, 0)
    
    def test_user_level_title(self):
        # Тестируем получение названия уровня
        title = self.user.get_level_title()
        self.assertIsInstance(title, str)
        self.assertGreater(len(title), 0)
    
    def test_user_achievements_count(self):
        # Создаем достижения для пользователя
        from game.models import Achievement, UserAchievement
        
        achievement1 = Achievement.objects.create(
            name='Достижение 1',
            description='Описание 1'
        )
        achievement2 = Achievement.objects.create(
            name='Достижение 2',
            description='Описание 2'
        )
        
        UserAchievement.objects.create(user=self.user, achievement=achievement1)
        UserAchievement.objects.create(user=self.user, achievement=achievement2)
        
        count = self.user.get_achievements_count()
        self.assertEqual(count, 2)
    
    def test_user_level_progress(self):
        # Создаем тему и уровни
        from game.models import Topic, Level, UserLevelProgress
        
        topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        level1 = Level.objects.create(
            title='Уровень 1',
            topic=topic,
            type='quiz',
            order_in_topic=1
        )
        
        level2 = Level.objects.create(
            title='Уровень 2',
            topic=topic,
            type='quiz',
            order_in_topic=2
        )
        
        # Создаем прогресс
        UserLevelProgress.objects.create(
            user=self.user,
            level=level1,
            completed=True,
            score=100
        )
        
        UserLevelProgress.objects.create(
            user=self.user,
            level=level2,
            completed=False,
            score=0
        )
        
        progress = self.user.get_level_progress()
        self.assertIsInstance(progress, (dict, int))
        if isinstance(progress, dict):
            self.assertIn('total_levels', progress)
            self.assertIn('completed_levels', progress)
            self.assertEqual(progress['total_levels'], 2)
            self.assertEqual(progress['completed_levels'], 1)
        else:
            # Если метод возвращает число, проверяем что это валидное значение
            self.assertGreaterEqual(progress, 0)

class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_data(self):
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'newpass123',
            'password2': 'differentpass'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_save(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpass123'))

class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')
    
    def test_login_view_post_valid_credentials(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа
        self.assertRedirects(response, '/')
    
    def test_login_view_post_invalid_credentials(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Остается на странице логина
        self.assertContains(response, 'Вход')
    
    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 200)  # Показывает страницу выхода
        self.assertContains(response, 'До свидания!')
        self.assertContains(response, 'Спасибо, что изучали финансы')
    
    def test_register_view_get(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
    
    def test_register_view_post_valid_data(self):
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешной регистрации
        
        # Проверяем, что пользователь создался
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
    
    def test_register_view_post_invalid_data(self):
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'newpass123',
            'password2': 'differentpass'
        })
        self.assertEqual(response.status_code, 200)  # Остается на странице регистрации
        self.assertContains(response, 'Регистрация')
    
    def test_register_view_duplicate_username(self):
        # Создаем пользователя с таким же именем
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        response = self.client.post('/accounts/register/', {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)  # Остается на странице регистрации
        self.assertContains(response, 'Регистрация')

class ProfileViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_view_requires_login(self):
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 302)  # Редирект на логин
    
    def test_profile_view_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Профиль')
        self.assertContains(response, 'testuser')
    
    def test_settings_view_requires_login(self):
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 302)  # Редирект на логин
    
    def test_settings_view_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Настройки')
    
    def test_settings_view_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/settings/', {
            'notifications_enabled': False
        })
        self.assertEqual(response.status_code, 302)  # Редирект после сохранения
        
        # Проверяем, что настройки сохранились
        user = User.objects.get(username='testuser')
        self.assertFalse(user.notifications_enabled)
    
    def test_reset_progress_view_requires_login(self):
        response = self.client.get('/accounts/reset/')
        self.assertEqual(response.status_code, 302)  # Редирект на логин
    
    def test_reset_progress_view_when_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Создаем прогресс пользователя
        from game.models import Topic, Level, UserLevelProgress, UserAchievement, Achievement
        
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
        
        UserLevelProgress.objects.create(
            user=self.user,
            level=level,
            completed=True,
            score=100
        )
        
        achievement = Achievement.objects.create(
            name='Тестовое достижение',
            description='Описание'
        )
        
        UserAchievement.objects.create(
            user=self.user,
            achievement=achievement
        )
        
        # Устанавливаем очки и монеты
        self.user.points = 1000
        self.user.coins = 500
        self.user.level_number = 5
        self.user.save()
        
        # Выполняем сброс прогресса
        response = self.client.post('/accounts/reset/')
        self.assertEqual(response.status_code, 302)  # Редирект на профиль
        
        # Проверяем, что прогресс сброшен
        user = User.objects.get(username='testuser')
        self.assertEqual(user.points, 0)
        self.assertEqual(user.coins, 0)
        self.assertEqual(user.level_number, 1)
        
        # Проверяем, что прогресс и достижения удалены
        self.assertFalse(UserLevelProgress.objects.filter(user=user).exists())
        self.assertFalse(UserAchievement.objects.filter(user=user).exists())

class UserIntegrationTest(TestCase):
    """Интеграционные тесты для пользователей"""
    
    def setUp(self):
        self.client = Client()
    
    def test_complete_user_registration_flow(self):
        """Тестирует полный процесс регистрации пользователя"""
        
        # 1. Переход на страницу регистрации
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        
        # 2. Заполнение формы регистрации
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. Проверка, что пользователь создался
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.points, 0)
        self.assertEqual(user.coins, 0)
        self.assertEqual(user.level_number, 1)
        self.assertTrue(user.notifications_enabled)
        
        # 4. Автоматический вход после регистрации
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дашборд')
    
    def test_user_settings_update(self):
        """Тестирует обновление настроек пользователя"""
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Обновляем настройки
        response = self.client.post('/accounts/settings/', {
            'notifications_enabled': False
        })
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что настройки обновились
        user.refresh_from_db()
        self.assertFalse(user.notifications_enabled)
        
        # Включаем уведомления обратно
        response = self.client.post('/accounts/settings/', {
            'notifications_enabled': True
        })
        self.assertEqual(response.status_code, 302)
        
        user.refresh_from_db()
        self.assertTrue(user.notifications_enabled)
    
    def test_user_progress_tracking(self):
        """Тестирует отслеживание прогресса пользователя"""
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем тестовые данные
        from game.models import Topic, Level, UserLevelProgress, Achievement, UserAchievement
        
        topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics'
        )
        
        level1 = Level.objects.create(
            title='Уровень 1',
            topic=topic,
            type='quiz',
            order_in_topic=1
        )
        
        level2 = Level.objects.create(
            title='Уровень 2',
            topic=topic,
            type='quiz',
            order_in_topic=2
        )
        
        achievement = Achievement.objects.create(
            name='Тестовое достижение',
            description='Описание'
        )
        
        # Создаем прогресс
        UserLevelProgress.objects.create(
            user=user,
            level=level1,
            completed=True,
            score=100
        )
        
        UserLevelProgress.objects.create(
            user=user,
            level=level2,
            completed=False,
            score=50
        )
        
        UserAchievement.objects.create(
            user=user,
            achievement=achievement
        )
        
        # Проверяем методы пользователя
        progress = user.get_level_progress()
        self.assertEqual(progress['total_levels'], 2)
        self.assertEqual(progress['completed_levels'], 1)
        
        achievements_count = user.get_achievements_count()
        self.assertEqual(achievements_count, 1)
        
        level_number = user.get_level_number()
        self.assertIsInstance(level_number, int)
        self.assertGreater(level_number, 0)
        
        level_title = user.get_level_title()
        self.assertIsInstance(level_title, str)
        self.assertGreater(len(level_title), 0)