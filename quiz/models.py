from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='📚')
    color = models.CharField(max_length=7, default='#6366f1')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    time_limit = models.IntegerField(default=30, help_text='Секунд на вопрос')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    play_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Викторина'
        verbose_name_plural = 'Викторины'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def difficulty_color(self):
        colors = {'easy': '#22c55e', 'medium': '#f59e0b', 'hard': '#ef4444'}
        return colors.get(self.difficulty, '#6366f1')

    @property
    def difficulty_label(self):
        labels = {'easy': 'Лёгкий', 'medium': 'Средний', 'hard': 'Сложный'}
        return labels.get(self.difficulty, 'Средний')


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True, help_text='Объяснение правильного ответа')
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=10)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self):
        return self.text[:80]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_correct else '✗'})"


class QuizSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    current_question = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    time_spent = models.IntegerField(default=0, help_text='Секунд')

    class Meta:
        verbose_name = 'Сессия викторины'
        verbose_name_plural = 'Сессии викторин'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} — {self.quiz.title}"

    @property
    def accuracy(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_count / self.total_questions) * 100)

    @property
    def percentage(self):
        return self.accuracy


class UserAnswer(models.Model):
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0, help_text='Секунд')
    points_earned = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'
