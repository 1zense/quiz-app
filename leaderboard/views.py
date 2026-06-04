from django.shortcuts import render
from django.db.models import Count, Avg
from accounts.models import User
from quiz.models import QuizSession
from .models import LeaderboardEntry


def leaderboard_view(request):
    period = request.GET.get('period', 'all')
    top_users = User.objects.order_by('-total_points')[:20]
    leaderboard_data = []
    for i, user in enumerate(top_users, 1):
        sessions = QuizSession.objects.filter(user=user, is_completed=True)
        leaderboard_data.append({
            'rank': i,
            'user': user,
            'points': user.total_points,
            'quizzes': user.quizzes_completed,
            'accuracy': user.accuracy,
            'is_current': request.user.is_authenticated and user == request.user,
        })
    user_rank = None
    if request.user.is_authenticated:
        better_users = User.objects.filter(total_points__gt=request.user.total_points).count()
        user_rank = better_users + 1
    return render(request, 'leaderboard/leaderboard.html', {
        'leaderboard_data': leaderboard_data,
        'user_rank': user_rank,
        'period': period,
    })
