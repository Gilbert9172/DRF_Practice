from django.urls import path
from .views import (
    RegisterView, VerifyEmail, LoginAPIView, 
    UpdatePassword, UserDetailView,
    EmailFindAPIView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('change/', UpdatePassword.as_view(), name="change"),
    path('detail/', UserDetailView.as_view(), name="detail" ),
    path('find-email/', EmailFindAPIView.as_view(), name="find-email")
]