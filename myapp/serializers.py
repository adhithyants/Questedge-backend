from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserDetail, Attempt

class UserDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    quiz_type = serializers.ChoiceField(
        choices=['multiple_choice', 'true_false'],
        write_only=True,
        required=False
    )
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserDetail
        fields = ['user_id', 'username', 'name', 'email', 'password', 'confirm_password', 'quiz_type', 'avg_technical_score', 'avg_aptitude_score', 'total_score', 'auth_user_id']
        read_only_fields = ['user_id', 'username', 'avg_technical_score', 'avg_aptitude_score', 'total_score', 'auth_user_id']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        email = data.get('email')
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists"})
        
        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        quiz_type = validated_data.pop('quiz_type', None)
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user_detail = UserDetail.objects.create(
            user=user,
            auth_user_id=user.id,
            **validated_data
        )
        return user_detail

class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ['id', 'user', 'auth_user_id', 'technical_marks', 'aptitude_marks', 'marks', 'attempt_date', 'category']
        read_only_fields = ['id', 'user', 'auth_user_id', 'marks', 'attempt_date']

    def validate(self, data):
        if data.get('technical_marks', 0) < 0:
            raise serializers.ValidationError({"technical_marks": "Technical marks cannot be negative."})
        if data.get('aptitude_marks', 0) < 0:
            raise serializers.ValidationError({"aptitude_marks": "Aptitude marks cannot be negative."})
        return data

    def create(self, validated_data):
        validated_data['user'] = UserDetail.objects.get(user__email=validated_data['email'])
        validated_data['auth_user_id'] = validated_data['user'].user
        return super().create(validated_data)