#!/usr/bin/env python
"""
Скрипт для запуска всех тестов приложения FinQuest
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Настройка Django для запуска тестов"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finquest.settings')
    django.setup()

def run_tests():
    """Запуск всех тестов"""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Список всех тестовых модулей
    test_modules = [
        'accounts.tests',
        'accounts.test_forms',
        'game.tests',
        'game.management.commands.test_management_commands',
        'finquest.test_urls',
        'finquest.test_templates',
    ]
    
    print("🧪 Запуск тестов FinQuest...")
    print("=" * 50)
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ Тесты завершились с ошибками: {failures}")
        return False
    else:
        print("\n✅ Все тесты прошли успешно!")
        return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
