# game/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fa-graduation-cap")  # для иконок (Font Awesome)

    def __str__(self):
        return self.name

class Level(models.Model):
    TOPIC_CHOICES = [
        ('savings', 'Накопления'),
        ('security', 'Базовая безопасность'),
        ('scam', 'Противодействие мошенничеству'),
        ('goals', 'Финансовые цели'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()  # введение перед уровнем
    difficulty = models.IntegerField(choices=[(1, 'Легко'), (2, 'Средне'), (3, 'Сложно')], default=1)
    order_in_topic = models.PositiveIntegerField()  # порядок в теме
    reward_points = models.IntegerField(default=10)
    reward_coins = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.topic.name} — {self.title}"

class LevelOption(models.Model):
    level = models.ForeignKey(Level, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text

class UserLevelProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)  # 0–100%
    attempts = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'level')

    def __str__(self):
        return f"{self.user.username} — {self.level.title} ({'✓' if self.completed else '✗'})"