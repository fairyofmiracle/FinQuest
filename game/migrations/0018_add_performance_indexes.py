# Generated migration for adding performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0017_topic_is_subcategory_topic_parent_category'),
    ]

    operations = [
        # Индексы для UserLevelProgress
        migrations.AddIndex(
            model_name='userlevelprogress',
            index=models.Index(fields=['user', 'completed'], name='game_userlv_user_id_compl_idx'),
        ),
        migrations.AddIndex(
            model_name='userlevelprogress',
            index=models.Index(fields=['level', 'user'], name='game_userlv_level_user_idx'),
        ),
        migrations.AddIndex(
            model_name='userlevelprogress',
            index=models.Index(fields=['-best_score'], name='game_userlv_best_sc_idx'),
        ),
        
        # Индексы для Level
        migrations.AddIndex(
            model_name='level',
            index=models.Index(fields=['topic', 'order_in_topic'], name='game_level_topic_order_idx'),
        ),
        migrations.AddIndex(
            model_name='level',
            index=models.Index(fields=['type'], name='game_level_type_idx'),
        ),
        
        # Индексы для Notification
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='game_notifi_user_isread_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['-created_at'], name='game_notifi_created_idx'),
        ),
        
        # Индексы для UserAchievement
        migrations.AddIndex(
            model_name='userachievement',
            index=models.Index(fields=['user', 'achievement'], name='game_userac_user_achiev_idx'),
        ),
        migrations.AddIndex(
            model_name='userachievement',
            index=models.Index(fields=['-earned_at'], name='game_userac_earned_idx'),
        ),
        
        # Индексы для Topic
        migrations.AddIndex(
            model_name='topic',
            index=models.Index(fields=['is_subcategory', 'parent_category'], name='game_topic_subcat_parent_idx'),
        ),
        migrations.AddIndex(
            model_name='topic',
            index=models.Index(fields=['main_category'], name='game_topic_maincat_idx'),
        ),
        
        # Индексы для Leaderboard
        migrations.AddIndex(
            model_name='leaderboard',
            index=models.Index(fields=['-total_score'], name='game_leaderb_score_idx'),
        ),
        migrations.AddIndex(
            model_name='leaderboard',
            index=models.Index(fields=['-updated_at'], name='game_leaderb_updated_idx'),
        ),
        
        # Индексы для DailyQuest (если есть)
        migrations.AddIndex(
            model_name='dailyquest',
            index=models.Index(fields=['quest_date', 'level'], name='game_dailyq_date_level_idx'),
        ),
    ]

