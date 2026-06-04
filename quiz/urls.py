from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('quizzes/', views.quiz_list_view, name='list'),
    path('quizzes/<int:pk>/', views.quiz_detail_view, name='detail'),
    path('quizzes/<int:pk>/start/', views.quiz_start_view, name='start'),
    path('play/<int:session_id>/', views.quiz_play_view, name='play'),
    path('play/<int:session_id>/submit/', views.submit_answer_view, name='submit'),
    path('play/<int:session_id>/finish/', views.quiz_finish_view, name='finish'),
    path('result/<int:session_id>/', views.quiz_result_view, name='result'),
]
