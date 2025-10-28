from django.contrib import admin
from django.utils.html import format_html
from django.forms import Textarea
from django.db import models
from .models import (
    Topic, Level, LevelOption, UserLevelProgress, Achievement, 
    UserAchievement, Streak, Notification, Hint, Article, 
    AvatarItem, Leaderboard, DailyQuest, UserDailyProgress
)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'main_category', 'order_in_category', 'is_active']
    list_filter = ['main_category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['main_category', 'order_in_category']
    list_editable = ['order_in_category', 'is_active']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'type', 'difficulty', 'order_in_topic', 'reward_points', 'reward_coins']
    list_filter = ['type', 'difficulty', 'topic__main_category']
    search_fields = ['title', 'description', 'topic__name']
    ordering = ['topic', 'order_in_topic']
    list_editable = ['difficulty', 'order_in_topic', 'reward_points', 'reward_coins']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'title', 'description', 'type', 'difficulty')
        }),
        ('Порядок и награды', {
            'fields': ('order_in_topic', 'reward_points', 'reward_coins')
        }),
        ('Контент уровня', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
    )
    
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('topic')

class LevelOptionInline(admin.TabularInline):
    model = LevelOption
    extra = 0
    fields = ['text', 'is_correct', 'order', 'question_number', 'hint']
    ordering = ['question_number', 'order']

class LevelWithOptionsAdmin(LevelAdmin):
    inlines = [LevelOptionInline]

# Регистрируем Level с опциями
admin.site.unregister(Level)
admin.site.register(Level, LevelWithOptionsAdmin)

@admin.register(LevelOption)
class LevelOptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'level', 'is_correct', 'question_number', 'order']
    list_filter = ['is_correct', 'level__topic', 'question_number']
    search_fields = ['text', 'level__title']
    ordering = ['level', 'question_number', 'order']
    list_editable = ['is_correct', 'order']

@admin.register(UserLevelProgress)
class UserLevelProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'completed', 'score', 'best_score', 'attempts', 'completion_time', 'best_time']
    list_filter = ['completed', 'level__topic', 'level__type']
    search_fields = ['user__username', 'level__title']
    readonly_fields = ['completion_time', 'best_time']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['achievement__category', 'earned_at']
    search_fields = ['user__username', 'achievement__name']
    readonly_fields = ['earned_at']
    ordering = ['-earned_at']

@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'last_activity']
    search_fields = ['user__username']
    readonly_fields = ['last_activity']
    ordering = ['-current_streak']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    list_display = ['level', 'text', 'cost_coins']
    search_fields = ['level__title', 'text']
    list_filter = ['level__topic']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'created_at']
    list_filter = ['topic', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']

@admin.register(AvatarItem)
class AvatarItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost_coins']
    search_fields = ['name', 'description']

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username']

@admin.register(DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'quest_type', 'target_value', 'reward_points', 'reward_coins', 'is_active']
    list_filter = ['quest_type', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active']

@admin.register(UserDailyProgress)
class UserDailyProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'quest', 'date']
    list_filter = ['date', 'quest__quest_type']
    search_fields = ['user__username', 'quest__title']
    ordering = ['-date']