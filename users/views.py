from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from users.models import CustomUser
from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationRequestSerializer,
    ConfirmationVerifySerializer
)
import random
import string
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            is_active=False
        )

        return Response({'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)

class SendConfirmationCodeAPIView(APIView):
    def post(self, request):
        serializer = ConfirmationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = ''.join(random.choices(string.digits, k=6))
        redis_key = f"confirm_code:{email}"

        redis_client.delete(redis_key)  # удалить старый код, если есть
        redis_client.setex(redis_key, 300, code)  # установить новый код с TTL 5 минут

        return Response({'message': 'Код отправлен на email', 'code': code}, status=200)

class ConfirmUserAPIView(APIView):
    def post(self, request):
        serializer = ConfirmationVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        redis_key = f"confirm_code:{email}"
        stored_code = redis_client.get(redis_key)

        if stored_code is None or stored_code.decode() != code:
            return Response({'error': 'Неверный или истекший код!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден!'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()
        redis_client.delete(redis_key)

        return Response({'message': 'Пользователь успешно подтвержден!'}, status=200)
