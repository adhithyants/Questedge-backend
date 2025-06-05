from django.urls import path
from . import views
from django.urls import path
from .views import SignupUser, SubmitAttempt, Leaderboard


app_name = 'myapp'

urlpatterns = [
    # Single endpoint for all quiz types
    path('quiz/<str:quiz_type>/', views.quiz_view, name='quiz'),
    path('signup/', SignupUser.as_view(), name='signup'),
    path('register/', views.SignupUser.as_view(), name='signup'),
    path('submit-attempt/', SubmitAttempt.as_view(), name='submit_attempt'),
    path('api/leaderboard/', Leaderboard.as_view(), name='leaderboard'),
]
