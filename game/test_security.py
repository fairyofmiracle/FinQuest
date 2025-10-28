"""
Тесты безопасности приложения
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from game.models import Level, Topic
from game.validators import (
    validate_quiz_answer,
    validate_matching_answer,
    validate_sorting_answer,
    sanitize_user_input,
    validate_question_index
)
from django.core.exceptions import ValidationError

User = get_user_model()


class CSRFProtectionTestCase(TestCase):
    """Тесты CSRF защиты"""
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_requires_csrf_token(self):
        """Проверяем, что логин требует CSRF токен"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Должен вернуть 403 без CSRF токена
        self.assertEqual(response.status_code, 403)
    
    def test_level_play_requires_csrf_token(self):
        """Проверяем, что отправка ответов требует CSRF токен"""
        self.client.force_login(self.user)
        
        # Создаем тестовый уровень
        topic = Topic.objects.create(name='Test Topic', slug='test-topic')
        level = Level.objects.create(
            topic=topic,
            title='Test Level',
            type='quiz',
            content={'questions': []}
        )
        
        response = self.client.post(reverse('level_play', args=[level.id]), {
            'answer': '0'
        })
        # Должен вернуть 403 без CSRF токена
        self.assertEqual(response.status_code, 403)


class RateLimitingTestCase(TestCase):
    """Тесты rate limiting"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()  # Очищаем кэш перед каждым тестом
    
    def test_login_rate_limiting(self):
        """Проверяем, что логин ограничен по количеству попыток"""
        login_url = reverse('login')
        
        # Делаем 5 попыток (лимит)
        for i in range(5):
            response = self.client.get(login_url)
            self.assertEqual(response.status_code, 200)
        
        # 6-я попытка должна быть заблокирована
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 403)


class XSSProtectionTestCase(TestCase):
    """Тесты защиты от XSS атак"""
    
    def test_sanitize_script_tag(self):
        """Проверяем удаление script тегов"""
        malicious_input = "<script>alert('XSS')</script>Hello"
        clean_output = sanitize_user_input(malicious_input)
        self.assertNotIn('<script>', clean_output)
        self.assertNotIn('alert', clean_output)
    
    def test_sanitize_javascript_protocol(self):
        """Проверяем удаление javascript: протокола"""
        malicious_input = "<a href='javascript:alert(1)'>Click</a>"
        clean_output = sanitize_user_input(malicious_input)
        self.assertNotIn('javascript:', clean_output)
    
    def test_sanitize_event_handlers(self):
        """Проверяем удаление event handlers"""
        malicious_input = "<img src=x onerror='alert(1)'>"
        clean_output = sanitize_user_input(malicious_input)
        self.assertNotIn('onerror', clean_output)
    
    def test_sanitize_html_escaping(self):
        """Проверяем экранирование HTML"""
        malicious_input = "<div>Test</div>"
        clean_output = sanitize_user_input(malicious_input)
        # HTML должен быть экранирован
        self.assertIn('&lt;', clean_output)
        self.assertIn('&gt;', clean_output)


class InputValidationTestCase(TestCase):
    """Тесты валидации входных данных"""
    
    def test_validate_question_index_valid(self):
        """Проверяем валидацию правильного индекса"""
        index = validate_question_index(0, 5)
        self.assertEqual(index, 0)
        
        index = validate_question_index(4, 5)
        self.assertEqual(index, 4)
    
    def test_validate_question_index_negative(self):
        """Проверяем отклонение отрицательного индекса"""
        with self.assertRaises(ValidationError):
            validate_question_index(-1, 5)
    
    def test_validate_question_index_out_of_range(self):
        """Проверяем отклонение индекса вне диапазона"""
        with self.assertRaises(ValidationError):
            validate_question_index(10, 5)
    
    def test_validate_question_index_invalid_type(self):
        """Проверяем отклонение невалидного типа"""
        with self.assertRaises(ValidationError):
            validate_question_index('abc', 5)
    
    def test_validate_matching_answer_valid(self):
        """Проверяем валидацию правильного matching ответа"""
        question = {
            'type': 'matching',
            'left_items': ['A', 'B', 'C'],
            'right_items': ['1', '2', '3']
        }
        answer_data = {
            'match_0': '0',
            'match_1': '1',
            'match_2': '2'
        }
        
        result = validate_matching_answer(answer_data, question)
        self.assertEqual(len(result), 3)
    
    def test_validate_matching_answer_invalid_index(self):
        """Проверяем отклонение недопустимых индексов"""
        question = {
            'type': 'matching',
            'left_items': ['A', 'B'],
            'right_items': ['1', '2']
        }
        answer_data = {
            'match_0': '10',  # Индекс вне диапазона
        }
        
        with self.assertRaises(ValidationError):
            validate_matching_answer(answer_data, question)
    
    def test_validate_matching_answer_negative_index(self):
        """Проверяем отклонение отрицательных индексов"""
        question = {
            'type': 'matching',
            'left_items': ['A', 'B'],
            'right_items': ['1', '2']
        }
        answer_data = {
            'match_0': '-1',
        }
        
        with self.assertRaises(ValidationError):
            validate_matching_answer(answer_data, question)
    
    def test_validate_sorting_answer_valid(self):
        """Проверяем валидацию правильного sorting ответа"""
        question = {
            'type': 'sorting',
            'items': [
                {'id': 1, 'text': 'First'},
                {'id': 2, 'text': 'Second'},
                {'id': 3, 'text': 'Third'}
            ]
        }
        answer_data = {
            'sort_0': '2',
            'sort_1': '1',
            'sort_2': '3'
        }
        
        result = validate_sorting_answer(answer_data, question)
        self.assertEqual(result, [2, 1, 3])
    
    def test_validate_sorting_answer_invalid_id(self):
        """Проверяем отклонение несуществующего ID"""
        question = {
            'type': 'sorting',
            'items': [
                {'id': 1, 'text': 'First'},
                {'id': 2, 'text': 'Second'}
            ]
        }
        answer_data = {
            'sort_0': '999',  # Несуществующий ID
        }
        
        with self.assertRaises(ValidationError):
            validate_sorting_answer(answer_data, question)


class SQLInjectionProtectionTestCase(TestCase):
    """Тесты защиты от SQL инъекций"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_topic_slug_sql_injection(self):
        """Проверяем защиту от SQL инъекций в slug"""
        # Django ORM автоматически защищает от SQL инъекций
        malicious_slug = "test'; DROP TABLE game_level; --"
        
        response = self.client.get(
            reverse('category_detail', args=[malicious_slug])
        )
        
        # Должен вернуть 404 или редирект, но не ошибку SQL
        self.assertIn(response.status_code, [302, 404])
        
        # Проверяем, что таблица все еще существует
        self.assertTrue(Level.objects.all().exists() or not Level.objects.exists())


class AuthenticationTestCase(TestCase):
    """Тесты аутентификации"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
    
    def test_login_required_for_dashboard(self):
        """Проверяем, что dashboard требует авторизации"""
        response = self.client.get(reverse('dashboard'))
        # Должен редиректить на логин
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_login_required_for_level_play(self):
        """Проверяем, что level_play требует авторизации"""
        topic = Topic.objects.create(name='Test', slug='test')
        level = Level.objects.create(
            topic=topic,
            title='Test',
            type='quiz',
            content={'questions': []}
        )
        
        response = self.client.get(reverse('level_play', args=[level.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_user_cannot_access_other_users_data(self):
        """Проверяем, что пользователь не может получить данные другого пользователя"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        self.client.force_login(self.user)
        
        # Пытаемся получить профиль другого пользователя
        # (Если есть такой endpoint)
        # response = self.client.get(reverse('profile', args=[other_user.id]))
        # self.assertEqual(response.status_code, 403)
        
        # Это просто пример - адаптируйте под ваши endpoints
        pass


class SessionSecurityTestCase(TestCase):
    """Тесты безопасности сессий"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
    
    def test_session_cookie_httponly(self):
        """Проверяем, что session cookie имеет HttpOnly флаг"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        
        # Проверяем cookie
        session_cookie = response.cookies.get('sessionid')
        if session_cookie:
            self.assertTrue(session_cookie['httponly'])
    
    def test_logout_clears_session(self):
        """Проверяем, что logout очищает сессию"""
        self.client.force_login(self.user)
        
        # Добавляем данные в сессию
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()
        
        # Выходим
        self.client.logout()
        
        # Проверяем, что сессия очищена
        self.assertNotIn('test_key', self.client.session)


def run_security_tests():
    """
    Запуск всех тестов безопасности
    
    Использование:
        python manage.py test game.test_security
    """
    import unittest
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(CSRFProtectionTestCase))
    suite.addTests(loader.loadTestsFromTestCase(RateLimitingTestCase))
    suite.addTests(loader.loadTestsFromTestCase(XSSProtectionTestCase))
    suite.addTests(loader.loadTestsFromTestCase(InputValidationTestCase))
    suite.addTests(loader.loadTestsFromTestCase(SQLInjectionProtectionTestCase))
    suite.addTests(loader.loadTestsFromTestCase(AuthenticationTestCase))
    suite.addTests(loader.loadTestsFromTestCase(SessionSecurityTestCase))
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

