from django.urls import path
from .views import quiz_view, SignupView, SubmitAttempt, AttemptListView, LoginView, SubmitAptitudeScore, leaderboard_view, UserEmailView, SignupUser,CreateRoomView, JoinRoomView ,loaderio_verification, RoomLeaderboardView, RoomResultListCreateView, RoomResultDetailView, RoomResultsByRoomView

app_name = 'myapp'

urlpatterns = [
    path('quiz/<str:quiz_type>/', quiz_view, name='quiz'),
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/signup-user/', SignupUser.as_view(), name='signup_user'),  # Added for SignupUser (optional)
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/submit-attempt/', SubmitAttempt.as_view(), name='submit_attempt'),
    path('api/submit-aptitude-score/', SubmitAptitudeScore.as_view(), name='submit_aptitude_score'),
    path('api/leaderboard/', leaderboard_view, name='leaderboard-api'),
    path('api/attempts/', AttemptListView.as_view(), name='attempt-list'),
    path('api/user-email/', UserEmailView.as_view(), name='user_email'),  # Added for UserEmailView
    path('create-room/', CreateRoomView.as_view(), name='create_room'),
    path('join-room/', JoinRoomView.as_view(), name='join_room'),
    path('api/room-leaderboard/<str:room_code>/', RoomLeaderboardView.as_view(), name='room_leaderboard'),
    path('loaderio-c506d955ab929b70b648697296775de0.txt', loaderio_verification),
    path('api/room-results/', RoomResultListCreateView.as_view(), name='roomresult-list-create'),
    path('api/room-results/<int:pk>/', RoomResultDetailView.as_view(), name='roomresult-detail'),
    path('api/room-results/by-room/<int:room_id>/', RoomResultsByRoomView.as_view(), name='roomresult-by-room'),
]
