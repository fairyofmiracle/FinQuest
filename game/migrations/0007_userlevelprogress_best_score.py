from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_avataritem_rename_message_notification_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlevelprogress',
            name='best_score',
            field=models.IntegerField(default=0),
        ),
    ]


