from django.db import models
from django.conf import settings


class LeaderboardEntry(models.Model):
    PERIOD_CHOICES = [
        ('all', 'За всё время'),
        ('month', 'За месяц'),
        ('week', 'За неделю'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaderboard_entries')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='all')
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    quizzes_completed = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'period')
        ordering = ['rank']
        verbose_name = 'Запись таблицы лидеров'
        verbose_name_plural = 'Таблица лидеров'

    def __str__(self):
        return f"{self.rank}. {self.user.username} — {self.points} очков"
