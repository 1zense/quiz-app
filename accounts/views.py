from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User, UserAchievement
from quiz.models import QuizSession


def register_view(request):
    if request.user.is_authenticated:
        return redirect('quiz:home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.username}! 🎉')
        return redirect('quiz:home')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('quiz:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'С возвращением, {user.username}! 👋')
        next_url = request.GET.get('next', 'quiz:home')
        return redirect(next_url)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    recent_sessions = QuizSession.objects.filter(
        user=user, is_completed=True
    ).select_related('quiz').order_by('-finished_at')[:5]
    achievements = UserAchievement.objects.filter(
        user=user
    ).select_related('achievement').order_by('-earned_at')
    stats = {
        'total_sessions': QuizSession.objects.filter(user=user, is_completed=True).count(),
        'avg_score': QuizSession.objects.filter(user=user, is_completed=True).aggregate(
            avg=Avg('score'))['avg'] or 0,
        'best_streak': QuizSession.objects.filter(user=user).aggregate(
            best=models_max('max_streak'))['best'] or 0,
    }
    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'recent_sessions': recent_sessions,
        'achievements': achievements,
        'stats': stats,
    })


@login_required
def edit_profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('accounts:profile')
    return render(request, 'accounts/edit_profile.html', {'form': form})


def public_profile_view(request, username):
    from django.shortcuts import get_object_or_404
    profile_user = get_object_or_404(User, username=username)
    recent_sessions = QuizSession.objects.filter(
        user=profile_user, is_completed=True
    ).select_related('quiz').order_by('-finished_at')[:5]
    achievements = UserAchievement.objects.filter(
        user=profile_user
    ).select_related('achievement')
    return render(request, 'accounts/public_profile.html', {
        'profile_user': profile_user,
        'recent_sessions': recent_sessions,
        'achievements': achievements,
    })


def models_max(field):
    from django.db.models import Max
    return Max(field)
