from django.urls import path
from users.views import (
    RegistrationAPIView,
    SendConfirmationCodeAPIView,
    ConfirmUserAPIView
)

urlpatterns = [
    path('register/', RegistrationAPIView.as_view()),
    path('send-code/', SendConfirmationCodeAPIView.as_view()),
    path('confirm/', ConfirmUserAPIView.as_view()),
]