from django.urls import path
from .views import quiz_view, SignupView, SubmitAttempt, Leaderboard, AttemptListView, LoginView, SubmitAptitudeScore

app_name = 'myapp'

urlpatterns = [
    path('quiz/<str:quiz_type>/', quiz_view, name='quiz'),
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/submit-attempt/', SubmitAttempt.as_view(), name='submit_attempt'),
    path('api/submit-aptitude-score/', SubmitAptitudeScore, name='submit_aptitude_score'),
    path('api/leaderboard/', Leaderboard.as_view(), name='leaderboard'),
    path('api/attempts/', AttemptListView.as_view(), name='attempt-list'),
]
