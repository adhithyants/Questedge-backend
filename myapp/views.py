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
from rest_framework.decorators import api_view, permission_classes  
from django.contrib.auth import authenticate 

CSRF_TRUSTED_ORIGINS = [
    "https://questedge.serveo.net"
]
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
        'pythoncode':'python_code.json',
        'javacode':'java_code.json',
        'javascriptcode':'javascript_code.json',
        'sqlcode':'sql_code.json',
        'htmlcode':'html_code.json',
        'grammar':'Grammer.json',
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

@api_view(['GET'])
def leaderboard_view(request):
    users = UserDetail.objects.order_by('-total_score')  # Top scorers first
    serializer = UserDetailSerializer(users, many=True)
    return Response(serializer.data)
        
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
    


class SubmitAptitudeScore(APIView):
    def post(self, request):
        try:
            score = request.data.get('score')
            category = request.data.get('category')
            email = request.data.get('email')  # Retrieve email from request body

            if not score or not category or not email:
                return Response({
                    'error': 'Score, category, and email are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user_detail = UserDetail.objects.get(user__email=email)
            except UserDetail.DoesNotExist:
                return Response({'error': 'UserDetail not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine which field to update based on category
            attempt_data = {
                'user': user_detail,
                'auth_user_id': user_detail.user,
                'category': category
            }
            if category.lower() == 'technical':
                attempt_data['technical_marks'] = score
                attempt_data['aptitude_marks'] = 0
            elif category.lower() == 'aptitude':
                attempt_data['aptitude_marks'] = score
                attempt_data['technical_marks'] = 0
            else:
                return Response({
                    'error': 'Invalid category. Must be "technical" or "aptitude"'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create attempt
            Attempt.objects.create(**attempt_data)

            return Response({
                'message': 'Score submitted successfully',
                'score': score,
                'category': category,
                'total_aptitude_score': user_detail.avg_aptitude_score,  # Adjust if renamed to total_aptitude_score
                'total_technical_score': user_detail.avg_technical_score,  # Adjust if renamed to total_technical_score
                'total_score': user_detail.total_score
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error submitting score: {str(e)}")
            return Response({'error': 'Server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            email = request.user.email
            if not email:
                return Response({'error': 'No email associated with this user'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'email': email}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching user email: {str(e)}")
            return Response({'error': 'Server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
