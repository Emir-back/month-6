from django.urls import path
from users.views import (
    RegistrationAPIView,
    AuthorizationAPIView,
    ConfirmUserAPIView,
    MyTokenView,
    GoogleLoginAPIView  
)

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view()),
    path('authorization/', AuthorizationAPIView.as_view()),
    path('confirm/', ConfirmUserAPIView.as_view()),
    path('token/', MyTokenView.as_view()),
    path('google-login/', GoogleLoginAPIView.as_view()),
]
