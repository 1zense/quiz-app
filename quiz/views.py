import json
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Avg, Max
from django.utils import timezone
from .models import Quiz, Category, Question, Answer, QuizSession, UserAnswer
from accounts.models import User, Achievement, UserAchievement
from django.conf import settings


def home_view(request):
    categories = Category.objects.annotate(quiz_count=Count('quizzes')).filter(quiz_count__gt=0)
    featured_quizzes = Quiz.objects.filter(is_active=True).select_related(
        'category', 'created_by'
    ).order_by('-play_count')[:6]
    top_users = User.objects.order_by('-total_points')[:5]
    stats = {
        'total_quizzes': Quiz.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'total_sessions': QuizSession.objects.filter(is_completed=True).count(),
    }
    return render(request, 'quiz/home.html', {
        'categories': categories,
        'featured_quizzes': featured_quizzes,
        'top_users': top_users,
        'stats': stats,
    })


@login_required
def quiz_list_view(request):
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    quizzes = Quiz.objects.filter(is_active=True).select_related('category', 'created_by').annotate(
        questions_total=Count('questions')
    )
    if category_id:
        quizzes = quizzes.filter(category_id=category_id)
    if difficulty:
        quizzes = quizzes.filter(difficulty=difficulty)
    categories = Category.objects.annotate(quiz_count=Count('quizzes'))
    return render(request, 'quiz/list.html', {
        'quizzes': quizzes.order_by('-play_count'),
        'categories': categories,
        'selected_category': category_id,
        'selected_difficulty': difficulty,
    })


@login_required
def quiz_detail_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
    user_sessions = QuizSession.objects.filter(
        user=request.user, quiz=quiz, is_completed=True
    ).order_by('-finished_at')[:3]
    best_score = user_sessions.aggregate(best=Max('score'))['best']
    return render(request, 'quiz/detail.html', {
        'quiz': quiz,
        'user_sessions': user_sessions,
        'best_score': best_score,
    })


@login_required
def quiz_start_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
    if quiz.question_count == 0:
        messages.error(request, 'Викторина не содержит вопросов.')
        return redirect('quiz:detail', pk=pk)
    session = QuizSession.objects.create(
        user=request.user,
        quiz=quiz,
        total_questions=quiz.question_count,
    )
    quiz.play_count += 1
    quiz.save(update_fields=['play_count'])
    return redirect('quiz:play', session_id=session.id)


@login_required
def quiz_play_view(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    if session.is_completed:
        return redirect('quiz:result', session_id=session_id)
    questions = list(session.quiz.questions.prefetch_related('answers').order_by('order'))
    if session.current_question >= len(questions):
        return redirect('quiz:finish', session_id=session_id)
    question = questions[session.current_question]
    answers = list(question.answers.all())
    return render(request, 'quiz/play.html', {
        'session': session,
        'question': question,
        'answers': answers,
        'question_number': session.current_question + 1,
        'total_questions': len(questions),
        'time_limit': session.quiz.time_limit,
        'progress': int((session.current_question / len(questions)) * 100),
    })


@login_required
def submit_answer_view(request, session_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    if session.is_completed:
        return JsonResponse({'error': 'Session completed'}, status=400)
    data = json.loads(request.body)
    answer_id = data.get('answer_id')
    time_taken = data.get('time_taken', 0)
    questions = list(session.quiz.questions.order_by('order'))
    if session.current_question >= len(questions):
        return JsonResponse({'error': 'No more questions'}, status=400)
    question = questions[session.current_question]
    answer = None
    is_correct = False
    points_earned = 0
    if answer_id:
        answer = get_object_or_404(Answer, id=answer_id, question=question)
        is_correct = answer.is_correct
    if is_correct:
        points_earned = question.points
        speed_bonus = 0
        if time_taken < 5:
            speed_bonus = settings.POINTS_BONUS_SPEED
        new_streak = session.streak + 1
        streak_bonus = (new_streak // 3) * settings.POINTS_BONUS_STREAK
        points_earned += speed_bonus + streak_bonus
        session.correct_count += 1
        session.score += points_earned
        session.streak = new_streak
        session.max_streak = max(session.max_streak, new_streak)
    else:
        session.streak = 0
    session.time_spent += time_taken
    UserAnswer.objects.create(
        session=session,
        question=question,
        answer=answer,
        is_correct=is_correct,
        time_taken=time_taken,
        points_earned=points_earned,
    )
    session.current_question += 1
    session.save()
    correct_answer = question.answers.filter(is_correct=True).first()
    return JsonResponse({
        'is_correct': is_correct,
        'points_earned': points_earned,
        'correct_answer_id': correct_answer.id if correct_answer else None,
        'explanation': question.explanation,
        'streak': session.streak,
        'total_score': session.score,
        'is_last': session.current_question >= len(questions),
    })


@login_required
def quiz_finish_view(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    if not session.is_completed:
        session.is_completed = True
        session.finished_at = timezone.now()
        session.save()
        _update_user_stats(request.user, session)
        new_achievements = _check_achievements(request.user)
        request.session['new_achievements'] = [a.id for a in new_achievements]
    return redirect('quiz:result', session_id=session_id)


@login_required
def quiz_result_view(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user, is_completed=True)
    user_answers = session.user_answers.select_related('question', 'answer').order_by('id')
    new_achievement_ids = request.session.pop('new_achievements', [])
    new_achievements = Achievement.objects.filter(id__in=new_achievement_ids) if new_achievement_ids else []
    best_session = QuizSession.objects.filter(
        user=request.user, quiz=session.quiz, is_completed=True
    ).order_by('-score').first()
    is_best = best_session and best_session.id == session.id
    return render(request, 'quiz/result.html', {
        'session': session,
        'user_answers': user_answers,
        'new_achievements': new_achievements,
        'is_best': is_best,
        'grade': _get_grade(session.accuracy),
    })


def _get_grade(accuracy):
    if accuracy >= 90: return ('S', '#ffd700')
    if accuracy >= 75: return ('A', '#22c55e')
    if accuracy >= 60: return ('B', '#3b82f6')
    if accuracy >= 40: return ('C', '#f59e0b')
    return ('D', '#ef4444')


def _update_user_stats(user, session):
    user.total_points += session.score
    user.quizzes_completed += 1
    user.correct_answers += session.correct_count
    user.total_answers += session.total_questions
    today = date.today()
    if user.last_activity == today:
        pass
    elif user.last_activity and (today - user.last_activity).days == 1:
        user.streak_days += 1
    else:
        user.streak_days = 1
    user.last_activity = today
    user.save()
    user.update_level()


def _check_achievements(user):
    new_achievements = []
    all_achievements = Achievement.objects.all()
    earned_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
    for ach in all_achievements:
        if ach.id in earned_ids:
            continue
        earned = False
        if ach.category == 'quiz' and user.quizzes_completed >= ach.requirement_value:
            earned = True
        elif ach.category == 'streak' and user.streak_days >= ach.requirement_value:
            earned = True
        elif ach.category == 'score' and user.total_points >= ach.requirement_value:
            earned = True
        elif ach.category == 'accuracy' and user.accuracy >= ach.requirement_value:
            earned = True
        if earned:
            UserAchievement.objects.create(user=user, achievement=ach)
            user.total_points += ach.points_reward
            user.achievements_count += 1
            new_achievements.append(ach)
    if new_achievements:
        user.save(update_fields=['total_points', 'achievements_count'])
        user.update_level()
    return new_achievements
