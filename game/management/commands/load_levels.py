#!/usr/bin/env python
import json
import os
from django.core.management.base import BaseCommand
from game.models import Topic, Level, LevelOption

class Command(BaseCommand):
    help = 'Load levels from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to JSON file with levels')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} not found'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        levels_created = 0
        levels_updated = 0

        for topic_data in data:
            topic_name = topic_data['topic']
            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                defaults={'description': f'Тема: {topic_name}'}
            )
            
            if created:
                self.stdout.write(f'Created topic: {topic_name}')
            else:
                self.stdout.write(f'Found existing topic: {topic_name}')

            for level_data in topic_data['levels']:
                level, created = Level.objects.get_or_create(
                    topic=topic,
                    title=level_data['title'],
                    defaults={
                        'type': level_data['type'],
                        'description': level_data['description'],
                        'difficulty': level_data['difficulty'],
                        'order_in_topic': level_data['order_in_topic'],
                        'reward_points': level_data['reward_points'],
                        'reward_coins': level_data['reward_coins'],
                        'content': level_data.get('content', {})
                    }
                )
                
                if created:
                    levels_created += 1
                    self.stdout.write(f'  Created level: {level.title}')
                else:
                    # Обновляем существующий уровень
                    level.type = level_data['type']
                    level.description = level_data['description']
                    level.difficulty = level_data['difficulty']
                    level.order_in_topic = level_data['order_in_topic']
                    level.reward_points = level_data['reward_points']
                    level.reward_coins = level_data['reward_coins']
                    level.content = level_data.get('content', {})
                    level.save()
                    levels_updated += 1
                    self.stdout.write(f'  Updated level: {level.title}')

                # Для старых типов уровней (quiz) создаем LevelOption
                if level_data['type'] == 'quiz' and 'content' in level_data:
                    content = level_data['content']
                    if 'options' in content:
                        # Удаляем старые опции
                        LevelOption.objects.filter(level=level).delete()
                        
                        # Создаем новые опции
                        for i, option_data in enumerate(content['options']):
                            LevelOption.objects.create(
                                level=level,
                                text=option_data['text'],
                                is_correct=option_data['is_correct'],
                                order=i + 1
                            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed levels: {levels_created} created, {levels_updated} updated'
            )
        )
