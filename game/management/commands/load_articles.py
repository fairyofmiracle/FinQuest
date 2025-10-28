#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from game.models import Article, Topic

class Command(BaseCommand):
    help = 'Загружает статьи из JSON файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='articles_data.json',
            help='Путь к JSON файлу со статьями'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие статьи перед загрузкой'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден!')
            )
            return

        # Очистка существующих статей
        if options['clear']:
            Article.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Существующие статьи удалены')
            )

        # Загрузка данных из JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        articles_data = data['articles']
        total_articles = 0

        for category_key, category_data in articles_data.items():
            self.stdout.write(f'Обрабатываем категорию: {category_data["name"]}')
            
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                self.stdout.write(f'  Подкатегория: {subcategory_data["name"]}')
                
                # Находим тему по названию
                try:
                    topic = Topic.objects.get(name=subcategory_data['name'])
                except Topic.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Тема "{subcategory_data["name"]}" не найдена, пропускаем'
                        )
                    )
                    continue

                # Создаем статьи
                for article_data in subcategory_data['articles']:
                    # Формируем контент статьи с дополнительной информацией
                    full_content = f"""
{article_data['summary']}

{article_data['content']}

---
Теги: {', '.join(article_data['tags'])}
Сложность: {article_data['difficulty']}
Время чтения: {article_data['reading_time']}
Автор: {article_data['author']}
"""
                    
                    article, created = Article.objects.get_or_create(
                        title=article_data['title'],
                        defaults={
                            'topic': topic,
                            'content': full_content.strip(),
                        }
                    )
                    
                    if created:
                        total_articles += 1
                        self.stdout.write(
                            f'    [СОЗДАНА] {article.title}'
                        )
                    else:
                        self.stdout.write(
                            f'    [СУЩЕСТВУЕТ] {article.title}'
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Загрузка завершена! Создано/обновлено статей: {total_articles}'
            )
        )

        # Статистика
        total_in_db = Article.objects.count()
        self.stdout.write(f'Всего статей в базе: {total_in_db}')
        
        # Статистика по темам
        self.stdout.write('\nСтатистика по темам:')
        for topic in Topic.objects.all():
            count = Article.objects.filter(topic=topic).count()
            if count > 0:
                self.stdout.write(f'  {topic.name}: {count} статей')
