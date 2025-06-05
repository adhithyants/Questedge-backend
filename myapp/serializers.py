# myapp/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserDetail, Attempt

class UserDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)  # For signup
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    quiz_type = serializers.ChoiceField(
        choices=['multiple_choice', 'true_false'],
        write_only=True,
        required=False
    )
    average_score = serializers.FloatField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)  # Add username
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Add user ID

    class Meta:
        model = UserDetail
        fields = ['user_id', 'username', 'name', 'email', 'password', 'confirm_password', 'quiz_type', 'average_score']

    def validate(self, data):
        # Validate password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        # Validate email uniqueness
        email = data.get('email')
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists"})
        
        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        quiz_type = validated_data.pop('quiz_type', None)  # Handle quiz_type if provided
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        # Create UserDetail
        user_detail = UserDetail.objects.create(user=user, **validated_data)
        # Optionally use quiz_type (e.g., store it or process it)
        return user_detail

class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ['technical_marks', 'aptitude_marks']