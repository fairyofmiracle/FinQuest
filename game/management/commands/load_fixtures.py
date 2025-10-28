#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загружает все фикстуры в правильном порядке'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед загрузкой'
        )
        parser.add_argument(
            '--fixtures-dir',
            type=str,
            default='game/fixtures',
            help='Директория с фикстурами'
        )

    def handle(self, *args, **options):
        fixtures_dir = options['fixtures_dir']
        
        if options['clear']:
            self.stdout.write('Очистка существующих данных...')
            # Очищаем в обратном порядке зависимостей
            call_command('shell', command='from game.models import *; LevelOption.objects.all().delete(); Level.objects.all().delete(); Topic.objects.all().delete()')
            self.stdout.write(self.style.WARNING('Данные очищены'))

        # Загружаем фикстуры в правильном порядке
        fixtures = [
            'topics.json',
            'levels.json', 
            'level_options.json'
        ]

        for fixture in fixtures:
            fixture_path = os.path.join(fixtures_dir, fixture)
            if os.path.exists(fixture_path):
                self.stdout.write(f'Загружаем {fixture}...')
                call_command('loaddata', fixture_path)
                self.stdout.write(self.style.SUCCESS(f'{fixture} загружен'))
            else:
                self.stdout.write(
                    self.style.ERROR(f'Файл {fixture_path} не найден!')
                )

        self.stdout.write(
            self.style.SUCCESS('Загрузка всех фикстур завершена!')
        )
