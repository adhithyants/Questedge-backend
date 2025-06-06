from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetail, Attempt
from .serializers import UserDetailSerializer, AttemptSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg, Count, Q
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated    

logger = logging.getLogger(__name__)

def load_quiz_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), 'quiz_data', filename)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading {filename}: {e}")
        return None

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def quiz_view(request, quiz_type):
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Request body: {request.body}")

    quiz_files = {
        'python': 'python_quiz.json',
        'html': 'html_quiz.json',
        'sql': 'sql_quiz.json',
        'java': 'java_quiz.json',
        'javascript': 'java_script_quiz.json',
        'logical-reasoning': 'logical_reasoning_quiz.json',
        'verbal-ability': 'verbal_ability_quiz.json',
        'abstract-reasoning': 'abstract_reasoning_quiz.json',
        'quantitative': 'quantitative_quiz.json',
        'technical': 'technical_quiz.json',
        'spatial-reasoning': 'spatial_reasoning_quiz.json',
    }

    filename = quiz_files.get(quiz_type)
    if not filename:
        logger.error(f"Invalid quiz type: {quiz_type}")
        return JsonResponse({'error': 'Invalid quiz type'}, status=400)

    quiz_data = load_quiz_data(filename)
    if quiz_data is None:
        logger.error(f"Quiz data not found or invalid for {filename}")
        return JsonResponse({'error': 'Quiz data not found or invalid'}, status=404)

    if request.method == 'GET':
        logger.info(f"Serving quiz data for {quiz_type}")
        return JsonResponse(quiz_data)
    elif request.method == 'POST':
        try:
            user_answers = json.loads(request.body.decode('utf-8'))
            logger.info(f"Received answers for {quiz_type}: {user_answers}")
            return JsonResponse({
                'message': 'Answers received successfully',
                'received_answers': user_answers
            })
        except json.JSONDecodeError:
            logger.error("Invalid JSON in POST request")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    elif request.method == 'OPTIONS':
        logger.info("Handling OPTIONS request")
        return HttpResponse('OPTIONS request allowed', status=200)

class SignupUser(APIView):
    def post(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            user_detail = serializer.save()
            refresh = RefreshToken.for_user(user_detail.user)
            return Response({
                'message': 'User registered successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubmitAttempt(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_detail = UserDetail.objects.get(user=request.user)
        except UserDetail.DoesNotExist:
            return Response({"error": "UserDetail not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttemptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user_detail, auth_user_id=request.user)
            return Response({"message": "Attempt recorded successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Leaderboard(APIView):
    def get(self, request):
        try:
            # Verify the relationship and field exist
            if not hasattr(UserDetail, 'attempts'):
                raise AttributeError("UserDetail model has no 'attempts' relation")
            
            # Safely build the queryset with proper field references
            users = UserDetail.objects.annotate(
                average_score=Avg('attempts__marks'),
                attempt_count=Count('attempts')
            ).filter(
                attempt_count__gt=0
            ).order_by('-average_score')[:100]

            serializer = UserDetailSerializer(users, many=True)
            
            leaderboard_data = []
            for index, user_data in enumerate(serializer.data, start=1):
                user_data['rank'] = index
                leaderboard_data.append(user_data)
            
            logger.info(f"Successfully fetched leaderboard with {len(leaderboard_data)} entries")
            return Response({
                'success': True,
                'data': leaderboard_data,
                'message': 'Leaderboard retrieved successfully'
            }, status=status.HTTP_200_OK)
            
        except AttributeError as e:
            logger.error(f"Model configuration error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Database configuration error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception("Error fetching leaderboard")
            return Response({
                'success': False,
                'error': 'Server error',
                'message': 'Failed to fetch leaderboard data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AttemptListView(generics.ListAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer

class SignupView(APIView):
    def post(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(username=email, password=password)
        if user:
            return Response(
                {"message": "Login successful", "user_id": user.id, "name": user.user_detail.name},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
class SubmitAptitudeScore(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            score = request.data.get('score')
            category = request.data.get('category')
            
            if score is None or category is None:
                return Response({
                    'error': 'Score and category are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the user's UserDetail
            try:
                user_detail = UserDetail.objects.get(user=request.user)
            except UserDetail.DoesNotExist:
                return Response({
                    'error': 'UserDetail not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Create a new attempt with the aptitude score
            attempt = Attempt.objects.create(
                user=user_detail,
                auth_user_id=request.user,
                technical_marks=0,  # Set to 0 for aptitude-only attempts
                aptitude_marks=score
            )

            # Update user's scores
            user_detail.update_scores()

            return Response({
                'message': 'Score submitted successfully',
                'score': score,
                'category': category,
                'average_score': user_detail.average_score(),
                'avg_aptitude_score': user_detail.avg_aptitude_score
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error submitting score: {str(e)}")
            return Response({
                'error': 'Failed to submit score',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
