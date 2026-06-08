from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak_days = models.IntegerField(default=0)
    last_activity = models.DateField(null=True, blank=True)
    quizzes_completed = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)
    achievements_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    @property
    def accuracy(self):
        if self.total_answers == 0:
            return 0
        return round((self.correct_answers / self.total_answers) * 100, 1)

    @property
    def level_name(self):
        levels = {
            1: "Новичок",
            2: "Ученик",
            3: "Знаток",
            4: "Эксперт",
            5: "Мастер",
            6: "Гуру",
            7: "Легенда",
        }
        return levels.get(min(self.level, 7), "Легенда")

    @property
    def points_to_next_level(self):
        thresholds = [0, 100, 300, 600, 1000, 1500, 2200, 3000]
        if self.level >= 7:
            return 0
        return thresholds[self.level] - self.total_points

    @property
    def level_progress(self):
        thresholds = [0, 100, 300, 600, 1000, 1500, 2200, 3000]
        if self.level >= 7:
            return 100
        prev = thresholds[self.level - 1]
        curr = thresholds[self.level]
        return int(((self.total_points - prev) / (curr - prev)) * 100)

    def update_level(self):
        thresholds = [0, 100, 300, 600, 1000, 1500, 2200, 3000]
        for i, threshold in enumerate(thresholds):
            if self.total_points >= threshold:
                self.level = i + 1
        self.save(update_fields=["level"])


class Achievement(models.Model):
    CATEGORY_CHOICES = [
        ("quiz", "Викторины"),
        ("streak", "Серии"),
        ("score", "Очки"),
        ("accuracy", "Точность"),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="🏆")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="quiz")
    points_reward = models.IntegerField(default=50)
    requirement_value = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_achievements"
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")
        verbose_name = "Достижение пользователя"
        verbose_name_plural = "Достижения пользователей"
