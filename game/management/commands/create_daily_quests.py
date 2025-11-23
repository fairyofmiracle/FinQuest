from django.core.management.base import BaseCommand
from game.models import DailyQuest
from datetime import date

class Command(BaseCommand):
    help = 'Создает ежедневные задания'

    def handle(self, *args, **options):
        # Удаляем старые задания
        DailyQuest.objects.all().delete()
        
        quests_data = [
            {
                'title': '🎯 Ежедневный ученик',
                'description': 'Пройди 3 уровня за день',
                'quest_type': 'levels_completed',
                'target_value': 3,
                'reward_coins': 50,
                'reward_points': 25,
            },
            {
                'title': '📚 Любитель знаний',
                'description': 'Прочитай 2 статьи',
                'quest_type': 'articles_read',
                'target_value': 2,
                'reward_coins': 30,
                'reward_points': 15,
            },
            {
                'title': '⭐ Охотник за очками',
                'description': 'Заработай 100 очков за день',
                'quest_type': 'points_earned',
                'target_value': 100,
                'reward_coins': 40,
                'reward_points': 20,
            },
            {
                'title': '🔥 Серия мастер',
                'description': 'Поддержи серию в 3 дня',
                'quest_type': 'streak_days',
                'target_value': 3,
                'reward_coins': 60,
                'reward_points': 30,
            },
            {
                'title': '🏆 Коллекционер достижений',
                'description': 'Получи 1 достижение',
                'quest_type': 'achievements_earned',
                'target_value': 1,
                'reward_coins': 80,
                'reward_points': 40,
            },
        ]
        
        for quest_data in quests_data:
            quest, created = DailyQuest.objects.get_or_create(
                title=quest_data['title'],
                defaults=quest_data
            )
            if created:
                # Убираем emoji для вывода в консоль Windows
                title_clean = quest_data['description']
                self.stdout.write(
                    self.style.SUCCESS(f'Создано задание: {title_clean}')
                )
            else:
                title_clean = quest_data['description']
                self.stdout.write(
                    self.style.WARNING(f'Задание уже существует: {title_clean}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Ежедневные задания созданы успешно!')
        )
