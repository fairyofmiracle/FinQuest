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
    LEVEL_TYPE_CHOICES = [
        ('quiz', 'Викторина'),
        ('scenario', 'Сценарий'),
        ('calculation', 'Расчеты'),
        ('matching', 'Сопоставление'),
        ('sorting', 'Сортировка'),
        ('simulation', 'Симуляция'),
        ('quest', 'Квест'),
    ]

    type = models.CharField(max_length=20, choices=LEVEL_TYPE_CHOICES, default='quiz')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()  # введение перед уровнем
    difficulty = models.IntegerField(choices=[(1, 'Легко'), (2, 'Средне'), (3, 'Сложно')], default=1)
    order_in_topic = models.PositiveIntegerField()  # порядок в теме
    reward_points = models.IntegerField(default=10)
    reward_coins = models.IntegerField(default=5)
    content = models.JSONField(default=dict, blank=True)  # Для хранения данных уровня

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
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)  # 0–100%
    best_score = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'level')

    def __str__(self):
        return f"{self.user.username} — {self.level.title} ({'✓' if self.completed else '✗'})"

class Achievement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    badge_image = models.ImageField(upload_to='badges/', blank=True, null=True)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')
        verbose_name = "Полученное достижение"
        verbose_name_plural = "Полученные достижения"

    def __str__(self):
        return f"{self.user} — {self.achievement}"


class Hint(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    text = models.TextField()
    cost_coins = models.IntegerField(default=5)

    def __str__(self):
        return f"Подсказка для {self.level.title}"

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.current_streak} дней"


class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user}: {self.text}"

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AvatarItem(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='avatars/items/')
    cost_coins = models.IntegerField(default=20)
    is_default = models.BooleanField(default=False)

class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard_entry')
    total_points = models.IntegerField(default=0)
    total_coins = models.IntegerField(default=0)
    levels_completed = models.IntegerField(default=0)
    achievements_count = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points', '-levels_completed', '-achievements_count']
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} очков"
    
    def get_rank(self):
        """Возвращает текущий ранг пользователя"""
        return Leaderboard.objects.filter(total_points__gt=self.total_points).count() + 1