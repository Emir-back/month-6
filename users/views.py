from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from .token import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationSerializer
)
from .models import ConfirmationCode, CustomUser
import random
import string
import requests 

User = get_user_model()

class MyTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class AuthorizationAPIView(APIView):
    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={'error': 'User account is not activated yet!'}
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={'key': token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={'error': 'User credentials are wrong!'}
        )

class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_active=False
            )

            code = ''.join(random.choices(string.digits, k=6))

            confirmation_code = ConfirmationCode.objects.create(
                user=user,
                code=code
            )

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'user_id': user.id,
                'confirmation_code': code
            }
        )

class ConfirmUserAPIView(APIView):
    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

            ConfirmationCode.objects.filter(user=user).delete()

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'User аккаунт успешно активирован',
                'key': token.key
            }
        )

class GoogleLoginAPIView(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token is required'}, status=400)

        google_user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        response = requests.get(google_user_info_url, params={'access_token': access_token})

        if response.status_code != 200:
            return Response({'error': 'Failed to fetch user info from Google'}, status=400)

        data = response.json()
        email = data.get('email')
        first_name = data.get('given_name')
        last_name = data.get('family_name')
        avatar = data.get('picture')

        if not email:
            return Response({'error': 'Email not provided by Google'}, status=400)

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email.split('@')[0],
            'is_active': True,
            'first_name': first_name,
            'last_name': last_name,
        })


        user.first_name = first_name
        user.last_name = last_name
        user.avatar_url = avatar
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
