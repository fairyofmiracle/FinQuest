# game/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Topic(models.Model):
    MAIN_CATEGORIES = [
        ('basics', 'Основы финансов'),
        ('security', 'Безопасность'),
        ('investments', 'Инвестиции'),
        ('planning', 'Планирование'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fa-graduation-cap")  # для иконок (Font Awesome)
    main_category = models.CharField(max_length=20, choices=MAIN_CATEGORIES, default='basics')
    order_in_category = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_subcategory = models.BooleanField(default=False)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['main_category', 'order_in_category']

class Level(models.Model):
    TOPIC_CHOICES = [
        ('savings', 'Накопления'),
        ('security', 'Базовая безопасность'),
        ('scam', 'Противодействие мошенничеству'),
        ('goals', 'Финансовые цели'),
    ]
    LEVEL_TYPE_CHOICES = [
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
    question_number = models.PositiveIntegerField(default=1)  # Номер вопроса
    hint = models.TextField(blank=True, null=True)  # Подсказка для варианта

    class Meta:
        ordering = ['question_number', 'order']

    def __str__(self):
        return self.text

class UserLevelProgress(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)  # 0–100%
    best_score = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)
    completion_time = models.IntegerField(default=0, help_text="Время прохождения в секундах")
    best_time = models.IntegerField(default=0, help_text="Лучшее время прохождения в секундах")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'level')

    def __str__(self):
        return f"{self.user.username} — {self.level.title} ({'✓' if self.completed else '✗'})"

class Achievement(models.Model):
    RARITY_CHOICES = [
        ('common', 'Обычная'),
        ('uncommon', 'Необычная'),
        ('rare', 'Редкая'),
        ('legendary', 'Легендарная'),
    ]
    
    CATEGORY_CHOICES = [
        ('progress', 'Прогресс'),
        ('streak', 'Серии'),
        ('points', 'Очки'),
        ('coins', 'Монеты'),
        ('levels', 'Уровни'),
        ('special', 'Особые'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='progress')
    badge_image = models.ImageField(upload_to='badges/', blank=True, null=True)
    icon = models.CharField(max_length=50, default="fa-trophy")  # Font Awesome иконка
    points_reward = models.IntegerField(default=0)  # Дополнительные очки за получение
    coins_reward = models.IntegerField(default=0)   # Дополнительные монеты за получение

    def __str__(self):
        return self.name
    
    def get_rarity_color(self):
        """Возвращает цвет рамки в зависимости от редкости"""
        colors = {
            'common': '#ffffff',      # Белый
            'uncommon': '#c0c0c0',    # Серебристый
            'rare': '#ffd700',        # Золотой
            'legendary': '#8b5cf6',   # Фиолетовый
        }
        return colors.get(self.rarity, '#ffffff')
    
    def get_rarity_class(self):
        """Возвращает CSS класс для редкости"""
        return f"achievement-{self.rarity}"


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


class DailyQuest(models.Model):
    """Ежедневные задания"""
    QUEST_TYPES = [
        ('levels_completed', 'Пройди уровни'),
        ('articles_read', 'Прочитай статьи'),
        ('points_earned', 'Заработай очки'),
        ('streak_days', 'Поддержи серию'),
        ('achievements_earned', 'Получи достижения'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    quest_type = models.CharField(max_length=20, choices=QUEST_TYPES)
    target_value = models.IntegerField()  # Целевое значение для выполнения
    reward_coins = models.IntegerField()  # Награда в монетах
    reward_points = models.IntegerField(default=0)  # Дополнительные очки
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserDailyProgress(models.Model):
    """Прогресс пользователя по ежедневным заданиям"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    quest = models.ForeignKey(DailyQuest, on_delete=models.CASCADE)
    current_progress = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'quest', 'date')
        verbose_name = "Прогресс по ежедневному заданию"
        verbose_name_plural = "Прогресс по ежедневным заданиям"

    def __str__(self):
        return f"{self.user.username} - {self.quest.title} ({self.current_progress}/{self.quest.target_value})"