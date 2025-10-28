# Generated manually for improved level types

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_daily_quests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='level',
            name='type',
            field=models.CharField(
                choices=[
                    ('quiz', 'Викторина'),
                    ('test', 'Тест'),
                    ('quest', 'Интерактивный квест'),
                    ('scenario', 'Сценарий'),
                    ('calculation', 'Финансовые расчеты'),
                    ('matching', 'Сопоставление'),
                    ('sorting', 'Сортировка'),
                    ('simulation', 'Симуляция'),
                    ('puzzle', 'Головоломка'),
                    ('story', 'История с выбором'),
                ],
                default='quiz',
                max_length=20
            ),
        ),
    ]
