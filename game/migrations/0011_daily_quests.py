# Generated manually for daily quests

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0010_level_content_alter_leaderboard_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyQuest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('quest_type', models.CharField(choices=[('levels_completed', 'Пройди уровни'), ('articles_read', 'Прочитай статьи'), ('points_earned', 'Заработай очки'), ('streak_days', 'Поддержи серию'), ('achievements_earned', 'Получи достижения')], max_length=20)),
                ('target_value', models.IntegerField()),
                ('reward_coins', models.IntegerField()),
                ('reward_points', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserDailyProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_progress', models.IntegerField(default=0)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('quest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.dailyquest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Прогресс по ежедневному заданию',
                'verbose_name_plural': 'Прогресс по ежедневным заданиям',
                'unique_together': {('user', 'quest', 'date')},
            },
        ),
    ]
