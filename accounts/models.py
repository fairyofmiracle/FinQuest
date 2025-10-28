from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    default_avatar = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('default1', 'Мечтатель'),
        ('default2', 'Новатор'),
        ('default3', 'Аналитик'),
        ('default4', 'Победитель'),
    ])
    avatar_border = models.CharField(max_length=20, default='novice', choices=[
        ('novice', 'Новичок'),
        ('beginner', 'Ученик'),
        ('intermediate', 'Защитник'),
        ('advanced', 'Эксперт'),
        ('expert', 'Мастер'),
        ('master', 'Гуру'),
        ('legend', 'Легенда'),
    ])
    points = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    level_number = models.IntegerField(default=1)
    notifications_enabled = models.BooleanField(default=True, verbose_name="Получать напоминания")


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # ← уникальное имя
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # ← уникальное имя
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def get_level_title(self):
        if self.points < 50:
            return "Новичок"
        elif self.points < 150:
            return "Ученик"
        elif self.points < 300:
            return "Защитник"
        elif self.points < 500:
            return "Эксперт"
        else:
            return "Мастер"
    
    def get_level_number(self):
        """Возвращает номер уровня пользователя"""
        if self.points < 50:
            return 1
        elif self.points < 150:
            return 2
        elif self.points < 300:
            return 3
        elif self.points < 500:
            return 4
        else:
            return 5
    
    def get_level_progress(self):
        """Возвращает прогресс текущего уровня в процентах"""
        if self.points < 50:
            return int((self.points / 50) * 100)
        elif self.points < 150:
            return int(((self.points - 50) / 100) * 100)
        elif self.points < 300:
            return int(((self.points - 150) / 150) * 100)
        elif self.points < 500:
            return int(((self.points - 300) / 200) * 100)
        else:
            return 100
    
    def get_achievements_count(self):
        """Возвращает количество полученных достижений"""
        from game.models import UserAchievement
        return UserAchievement.objects.filter(user=self).count()
    
    def get_unread_notifications_count(self):
        """Возвращает количество непрочитанных уведомлений"""
        from game.models import Notification
        return Notification.objects.filter(user=self, is_read=False).count()
    
    def get_avatar_border_class(self):
        """Возвращает CSS класс для рамки аватара в зависимости от выбранной рамки"""
        return f"avatar-border-{self.avatar_border}"
    
    def get_available_borders(self):
        """Возвращает доступные рамки в зависимости от уровня пользователя"""
        available = []
        if self.points >= 0:
            available.append(('novice', 'Новичок', 'Серый'))
        if self.points >= 50:
            available.append(('beginner', 'Ученик', 'Зеленый'))
        if self.points >= 150:
            available.append(('intermediate', 'Защитник', 'Синий'))
        if self.points >= 300:
            available.append(('advanced', 'Эксперт', 'Фиолетовый'))
        if self.points >= 500:
            available.append(('expert', 'Мастер', 'Оранжевый'))
        if self.points >= 1000:
            available.append(('master', 'Гуру', 'Красный'))
        if self.points >= 2000:
            available.append(('legend', 'Легенда', 'Золотой'))
        return available
    
    def get_avatar_display(self):
        """Возвращает аватар для отображения (загруженный или по умолчанию)"""
        if self.avatar:
            return self.avatar.url
        elif self.default_avatar:
            return f"/static/avatars/default/{self.default_avatar}.svg"
        else:
            return None