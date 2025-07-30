from rest_framework import serializers
from users.models import CustomUser

class ConfirmationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ConfirmationVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class AuthValidateSerializer(UserBaseSerializer):
    pass

class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email уже существует!')
        return email
