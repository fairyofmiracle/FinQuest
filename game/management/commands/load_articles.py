from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
import json
import os
from game.models import Article, Topic

class Command(BaseCommand):
    help = 'Загружает статьи из JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к JSON файлу со статьями')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'Файл {json_file} не найден!')
            )
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при чтении JSON файла: {e}')
            )
            return

        created_count = 0
        updated_count = 0
        error_count = 0

        for article_data in articles_data:
            try:
                # Получаем или создаем тему
                topic_name = article_data.get('topic', 'Общее')
                topic, _ = Topic.objects.get_or_create(
                    name=topic_name,
                    defaults={
                        'description': f'Статьи по теме "{topic_name}"',
                        'icon': 'fa-book'
                    }
                )

                # Создаем или обновляем статью
                article, created = Article.objects.get_or_create(
                    title=article_data['title'],
                    defaults={
                        'content': article_data['content'],
                        'topic': topic
                    }
                )

                if not created:
                    # Обновляем существующую статью
                    article.content = article_data['content']
                    article.topic = topic
                    article.save()
                    updated_count += 1
                    self.stdout.write('Обновлена статья')
                else:
                    created_count += 1
                    self.stdout.write('Создана статья')

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при обработке статьи: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово! Создано: {created_count}, обновлено: {updated_count}, ошибок: {error_count}'
            )
        )
