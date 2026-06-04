from django.contrib import admin
from .models import LeaderboardEntry

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'period', 'points', 'quizzes_completed')
    list_filter = ('period',)
