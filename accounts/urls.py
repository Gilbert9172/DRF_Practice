from django.urls import path
from .views import (
    RegisterView, VerifyEmail, LoginAPIView,UpdatePassword
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('change/<int:id>', UpdatePassword.as_view(), name="change")
]