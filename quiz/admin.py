from django.contrib import admin
from .models import Category, Quiz, Question, Answer, QuizSession, UserAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'play_count', 'is_active', 'created_at')
    list_filter = ('category', 'difficulty', 'is_active')
    inlines = [QuestionInline]
    search_fields = ('title', 'description')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'points', 'order')
    inlines = [AnswerInline]
    list_filter = ('quiz__category',)


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'correct_count', 'total_questions', 'is_completed', 'started_at')
    list_filter = ('is_completed', 'quiz__category')
    readonly_fields = ('started_at',)
