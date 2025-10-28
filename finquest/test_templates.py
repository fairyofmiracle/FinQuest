from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from game.models import Topic, Level, LevelOption, UserLevelProgress, Achievement, UserAchievement, Notification, DailyQuest, UserDailyProgress
from datetime import date

User = get_user_model()

class TemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_template(self):
        """Тестирует шаблон главной страницы"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FinQuest')
        self.assertContains(response, 'Финансовая грамотность')
        self.assertTemplateUsed(response, 'game/home.html')
    
    def test_dashboard_template(self):
        """Тестирует шаблон дашборда"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дашборд')
        self.assertTemplateUsed(response, 'game/dashboard.html')
    
    def test_login_template(self):
        """Тестирует шаблон входа"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_register_template(self):
        """Тестирует шаблон регистрации"""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_logout_template(self):
        """Тестирует шаблон выхода"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'До свидания!')
        self.assertContains(response, 'Спасибо, что изучали финансы')
        self.assertTemplateUsed(response, 'accounts/logged_out.html')
    
    def test_profile_template(self):
        """Тестирует шаблон профиля"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Профиль')
        self.assertContains(response, 'testuser')
        self.assertTemplateUsed(response, 'accounts/profile.html')
    
    def test_settings_template(self):
        """Тестирует шаблон настроек"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Настройки')
        self.assertTemplateUsed(response, 'accounts/settings.html')
    
    def test_media_template(self):
        """Тестирует шаблон медиа"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/media/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/media.html')
    
    def test_notifications_template(self):
        """Тестирует шаблон уведомлений"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/notifications.html')
    
    def test_daily_quests_template(self):
        """Тестирует шаблон ежедневных заданий"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/daily-quests/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/daily_quests.html')
    
    def test_leaderboard_template(self):
        """Тестирует шаблон рейтинга"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/leaderboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/leaderboard.html')

class LevelTemplatesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.topic = Topic.objects.create(
            name='Тестовая тема',
            main_category='basics',
            description='Описание тестовой темы'
        )
        
        self.level = Level.objects.create(
            title='Тестовый уровень',
            topic=self.topic,
            type='quiz',
            difficulty=1,
            order_in_topic=1,
            reward_points=10,
            reward_coins=5,
            description='Описание тестового уровня',
            content={'questions': [{'text': 'Тестовый вопрос', 'hint': 'Тестовая подсказка'}]}
        )
        
        self.option = LevelOption.objects.create(
            level=self.level,
            text='Правильный ответ',
            is_correct=True,
            order=1,
            question_number=1
        )
    
    def test_topic_levels_template(self):
        """Тестирует шаблон уровней темы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/topic/{self.topic.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.name)
        self.assertContains(response, self.level.title)
        self.assertTemplateUsed(response, 'game/topic_levels.html')
    
    def test_level_play_template(self):
        """Тестирует шаблон прохождения уровня"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{self.level.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.level.title)
        self.assertContains(response, self.level.description)
        self.assertContains(response, 'Правильный ответ')
        self.assertTemplateUsed(response, 'game/level_play_improved.html')
    
    def test_level_result_template(self):
        """Тестирует шаблон результата уровня"""
        # Создаем прогресс пользователя
        UserLevelProgress.objects.create(
            user=self.user,
            level=self.level,
            completed=True,
            score=100
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{self.level.id}/result/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.level.title)
        self.assertTemplateUsed(response, 'game/level_result.html')
    
    def test_level_play_quiz_template(self):
        """Тестирует шаблон викторины"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{self.level.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вопрос 1')
        self.assertContains(response, 'Правильный ответ')
        self.assertContains(response, 'Показать подсказку')
    
    def test_level_play_calculation_template(self):
        """Тестирует шаблон расчетов"""
        calculation_level = Level.objects.create(
            title='Тестовые расчеты',
            topic=self.topic,
            type='calculation',
            difficulty=2,
            order_in_topic=2,
            reward_points=20,
            reward_coins=10,
            description='Описание расчетов',
            content={
                'questions': [
                    {
                        'question': 'Сколько будет 2 + 2?',
                        'correct_answer': 4,
                        'tolerance': 0,
                        'hint': 'Простое сложение'
                    }
                ]
            }
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{calculation_level.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задача 1')
        self.assertContains(response, 'Сколько будет 2 + 2?')
        self.assertContains(response, 'Ваш ответ:')
    
    def test_level_play_scenario_template(self):
        """Тестирует шаблон сценария"""
        scenario_level = Level.objects.create(
            title='Тестовый сценарий',
            topic=self.topic,
            type='scenario',
            difficulty=3,
            order_in_topic=3,
            reward_points=25,
            reward_coins=15,
            description='Описание сценария',
            content={
                'scenario_text': 'Выберите правильный вариант',
                'options': [
                    {'text': 'Неправильный вариант'},
                    {'text': 'Правильный вариант'}
                ],
                'correct_answer': 1,
                'hint': 'Подумайте логически'
            }
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{scenario_level.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сценарий принятия решений')
        self.assertContains(response, 'Выберите правильный вариант')
        self.assertContains(response, 'Неправильный вариант')
        self.assertContains(response, 'Правильный вариант')

class TemplateContextTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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
    
    def test_dashboard_context(self):
        """Тестирует контекст дашборда"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/dashboard/')
        
        # Проверяем наличие ключей в контексте
        self.assertIn('topics', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('unread_notifications', response.context)
        self.assertIn('is_first_visit', response.context)
    
    def test_topic_levels_context(self):
        """Тестирует контекст уровней темы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/topic/{self.topic.id}/')
        
        # Проверяем наличие ключей в контексте
        self.assertIn('topic', response.context)
        self.assertIn('levels', response.context)
        
        # Проверяем значения
        self.assertEqual(response.context['topic'], self.topic)
        self.assertIn(self.level, response.context['levels'])
    
    def test_level_play_context(self):
        """Тестирует контекст прохождения уровня"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{self.level.id}/')
        
        # Проверяем наличие ключей в контексте
        self.assertIn('level', response.context)
        self.assertIn('options', response.context)
        self.assertIn('hint', response.context)
        self.assertIn('hint_shown', response.context)
        
        # Проверяем значения
        self.assertEqual(response.context['level'], self.level)
    
    def test_level_result_context(self):
        """Тестирует контекст результата уровня"""
        # Создаем прогресс пользователя
        progress = UserLevelProgress.objects.create(
            user=self.user,
            level=self.level,
            completed=True,
            score=100
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/level/{self.level.id}/result/')
        
        # Проверяем наличие ключей в контексте
        self.assertIn('level', response.context)
        self.assertIn('progress', response.context)
        self.assertIn('correct_option', response.context)
        self.assertIn('next_level', response.context)
        
        # Проверяем значения
        self.assertEqual(response.context['level'], self.level)
        self.assertEqual(response.context['progress'], progress)

class TemplateInheritanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_base_template_inheritance(self):
        """Тестирует наследование от базового шаблона"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_template_blocks(self):
        """Тестирует блоки шаблонов"""
        response = self.client.get('/')
        self.assertContains(response, 'FinQuest')
        self.assertContains(response, 'Финансовая грамотность')
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertContains(response, 'Дашборд')
        self.assertContains(response, 'testuser')

class TemplateStaticFilesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_static_files_loading(self):
        """Тестирует загрузку статических файлов"""
        response = self.client.get('/')
        self.assertContains(response, 'static/css/')
        self.assertContains(response, 'static/js/')
    
    def test_css_files_present(self):
        """Тестирует наличие CSS файлов"""
        response = self.client.get('/')
        self.assertContains(response, 'bootstrap.min.css')
        self.assertContains(response, 'finquest.css')
        self.assertContains(response, 'fontawesome.min.css')
    
    def test_js_files_present(self):
        """Тестирует наличие JS файлов"""
        response = self.client.get('/')
        self.assertContains(response, 'bootstrap.bundle.min.js')
        self.assertContains(response, 'finquest.js')

class TemplateResponsiveTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_responsive_classes(self):
        """Тестирует наличие responsive классов"""
        response = self.client.get('/')
        self.assertContains(response, 'container')
        self.assertContains(response, 'row')
        self.assertContains(response, 'col-')
    
    def test_bootstrap_classes(self):
        """Тестирует наличие Bootstrap классов"""
        response = self.client.get('/')
        self.assertContains(response, 'btn')
        self.assertContains(response, 'card')
        self.assertContains(response, 'text-center')
    
    def test_fontawesome_icons(self):
        """Тестирует наличие FontAwesome иконок"""
        response = self.client.get('/')
        self.assertContains(response, 'fa-')
        self.assertContains(response, 'fa-solid')
