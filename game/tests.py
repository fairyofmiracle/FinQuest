from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from game.models import Topic, Level, UserLevelProgress, Achievement, UserAchievement
from accounts.models import User
import json

class UserModelTest(TestCase):
    """Тесты для модели User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            points=0
        )
    
    def test_level_number_calculation(self):
        """Проверка расчета номера уровня"""
        # Уровень 1: 0-49 очков
        self.user.points = 25
        self.assertEqual(self.user.get_level_number(), 1)
        
        # Уровень 2: 50-149 очков
        self.user.points = 100
        self.assertEqual(self.user.get_level_number(), 2)
        
        # Уровень 3: 150-299 очков
        self.user.points = 200
        self.assertEqual(self.user.get_level_number(), 3)
        
        # Уровень 4: 300-499 очков
        self.user.points = 400
        self.assertEqual(self.user.get_level_number(), 4)
        
        # Уровень 5: 500+ очков
        self.user.points = 600
        self.assertEqual(self.user.get_level_number(), 5)
    
    def test_level_title(self):
        """Проверка названий уровней"""
        self.user.points = 25
        self.assertEqual(self.user.get_level_title(), "Новичок")
        
        self.user.points = 100
        self.assertEqual(self.user.get_level_title(), "Ученик")
        
        self.user.points = 200
        self.assertEqual(self.user.get_level_title(), "Защитник")
        
        self.user.points = 400
        self.assertEqual(self.user.get_level_title(), "Эксперт")
        
        self.user.points = 600
        self.assertEqual(self.user.get_level_title(), "Мастер")
    
    def test_level_progress_calculation(self):
        """Проверка расчета прогресса текущего уровня"""
        # Прогресс в уровне 1
        self.user.points = 25  # 50%
        self.assertEqual(self.user.get_level_progress(), 50)
        
        # Прогресс в уровне 2
        self.user.points = 100  # (100-50)/100 = 50%
        self.assertEqual(self.user.get_level_progress(), 50)
        
        # Максимальный уровень
        self.user.points = 600
        self.assertEqual(self.user.get_level_progress(), 100)


class LevelViewTest(TestCase):
    """Тесты для представлений уровней"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            points=0,
            coins=10
        )
        
        # Создаем тестовую тему и уровень
        self.topic = Topic.objects.create(
            title='Тестовая тема',
            description='Описание',
            main_category='basics'
        )
        
        self.level = Level.objects.create(
            topic=self.topic,
            title='Тестовый уровень',
            description='Описание уровня',
            order_in_topic=1,
            reward_points=10,
            reward_coins=5,
            type='quiz',
            content={
                'questions': [
                    {
                        'question': 'Тестовый вопрос?',
                        'type': 'single',
                        'options': [
                            {'text': 'Правильный ответ', 'correct': True},
                            {'text': 'Неправильный ответ', 'correct': False}
                        ]
                    }
                ]
            }
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_level_play_requires_login(self):
        """Проверка что уровень требует авторизации"""
        self.client.logout()
        response = self.client.get(reverse('level_play', args=[self.level.id]))
        self.assertEqual(response.status_code, 302)  # Редирект на login
    
    def test_level_play_access(self):
        """Проверка доступа к уровню"""
        response = self.client.get(reverse('level_play', args=[self.level.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.level.title)
    
    def test_level_completion(self):
        """Проверка прохождения уровня"""
        old_points = self.user.points
        old_level = self.user.level_number
        
        # Отправляем правильный ответ
        response = self.client.post(reverse('level_play', args=[self.level.id]), {
            'question_index': 0,
            'answer': 0,  # Индекс правильного ответа
            'completion_time': 30
        })
        
        # Обновляем данные пользователя из БД
        self.user.refresh_from_db()
        
        # Проверяем что очки начислены
        self.assertEqual(self.user.points, old_points + self.level.reward_points)
        self.assertEqual(self.user.coins, 10 + self.level.reward_coins)
        
        # Проверяем прогресс
        progress = UserLevelProgress.objects.get(user=self.user, level=self.level)
        self.assertTrue(progress.completed)
        self.assertEqual(progress.score, 100)
    
    def test_level_up_notification(self):
        """Проверка уведомления о повышении уровня"""
        # Устанавливаем очки близкие к следующему уровню
        self.user.points = 45  # До уровня 2 осталось 5 очков
        self.user.level_number = 1
        self.user.save()
        
        # Создаем уровень с наградой 10 очков
        level = Level.objects.create(
            topic=self.topic,
            title='Уровень для повышения',
            description='Описание',
            order_in_topic=2,
            reward_points=10,
            reward_coins=5,
            type='quiz',
            content={
                'questions': [
                    {
                        'question': 'Вопрос?',
                        'type': 'single',
                        'options': [
                            {'text': 'Ответ', 'correct': True}
                        ]
                    }
                ]
            }
        )
        
        # Проходим уровень
        response = self.client.post(reverse('level_play', args=[level.id]), {
            'question_index': 0,
            'answer': 0,
            'completion_time': 30
        }, follow=True)
        
        # Проверяем что в сессии есть данные о повышении
        session = self.client.session
        # Данные должны быть удалены после показа, но мы можем проверить уровень пользователя
        self.user.refresh_from_db()
        self.assertEqual(self.user.level_number, 2)


class MatchingSortingTest(TestCase):
    """Тесты для Matching и Sorting"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            points=0
        )
        
        self.topic = Topic.objects.create(
            title='Тестовая тема',
            main_category='basics'
        )
    
        # Создаем уровень с matching
        self.matching_level = Level.objects.create(
            topic=self.topic,
            title='Matching уровень',
            order_in_topic=1,
            reward_points=10,
            type='quiz',
            content={
                'questions': [
                    {
                        'question': 'Сопоставьте термины',
                        'type': 'matching',
                        'left_items': ['A', 'B', 'C'],
                        'right_items': ['1', '2', '3'],
                        'correct_matches': [[0, 0], [1, 1], [2, 2]]
                    }
                ]
            }
        )
        
        # Создаем уровень с sorting
        self.sorting_level = Level.objects.create(
            topic=self.topic,
            title='Sorting уровень',
            order_in_topic=2,
            reward_points=10,
            type='quiz',
            content={
                'questions': [
                    {
                        'question': 'Расположите по порядку',
                        'type': 'sorting',
                        'items': [
                            {'id': 1, 'text': 'Первый'},
                            {'id': 2, 'text': 'Второй'},
                            {'id': 3, 'text': 'Третий'}
                        ],
                        'correct_order': [1, 2, 3]
                    }
                ]
            }
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_matching_correct_answer(self):
        """Проверка правильного сопоставления"""
        response = self.client.post(reverse('level_play', args=[self.matching_level.id]), {
            'question_index': 0,
            'match_0': 0,
            'match_1': 1,
            'match_2': 2,
            'completion_time': 30
        }, follow=True)
        
        progress = UserLevelProgress.objects.get(user=self.user, level=self.matching_level)
        self.assertTrue(progress.completed)
        self.assertEqual(progress.score, 100)
    
    def test_matching_incorrect_answer(self):
        """Проверка неправильного сопоставления"""
        response = self.client.post(reverse('level_play', args=[self.matching_level.id]), {
            'question_index': 0,
            'match_0': 1,  # Неправильно
            'match_1': 0,  # Неправильно
            'match_2': 2,
            'completion_time': 30
        }, follow=True)
        
        progress = UserLevelProgress.objects.get(user=self.user, level=self.matching_level)
        self.assertFalse(progress.completed)
        self.assertEqual(progress.score, 0)
    
    def test_sorting_correct_answer(self):
        """Проверка правильной сортировки"""
        response = self.client.post(reverse('level_play', args=[self.sorting_level.id]), {
            'question_index': 0,
            'sort_0': 1,
            'sort_1': 2,
            'sort_2': 3,
            'completion_time': 30
        }, follow=True)
        
        progress = UserLevelProgress.objects.get(user=self.user, level=self.sorting_level)
        self.assertTrue(progress.completed)
        self.assertEqual(progress.score, 100)


class AchievementTest(TestCase):
    """Тесты для системы достижений"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            points=0
        )
        
        self.achievement = Achievement.objects.create(
            name='Первые шаги',
            description='Первый ответ',
            icon='trophy',
            rarity='common'
        )
    
    def test_achievement_creation(self):
        """Проверка создания достижения"""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        
        self.assertEqual(user_achievement.user, self.user)
        self.assertEqual(user_achievement.achievement, self.achievement)
        self.assertIsNotNone(user_achievement.unlocked_at)
    
    def test_get_achievements_count(self):
        """Проверка подсчета достижений"""
        self.assertEqual(self.user.get_achievements_count(), 0)
        
        UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        
        self.assertEqual(self.user.get_achievements_count(), 1)


# Запуск: python manage.py test game.tests
