from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    points = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    level_number = models.IntegerField(default=1)

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