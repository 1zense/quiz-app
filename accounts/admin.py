from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Achievement, UserAchievement


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'total_points', 'level', 'quizzes_completed', 'streak_days')
    list_filter = ('level', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Геймификация', {'fields': ('total_points', 'level', 'streak_days', 'last_activity',
                                     'quizzes_completed', 'correct_answers', 'total_answers', 'achievements_count')}),
        ('Профиль', {'fields': ('avatar', 'bio')}),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon', 'points_reward', 'requirement_value')
    list_filter = ('category',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement__category',)
