from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models.fields import BooleanField
from .managers import UserManager
from rest_framework_simplejwt.tokens import RefreshToken

#-- Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone = models.CharField(max_length=255, unique=True)
    
    Gender_Choice = (
        ("M", "남성"),
        ("F", "여성")
    )
    gender = models.CharField(max_length=1, choices=Gender_Choice, blank=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 로그인 ID로 사용되는 필드 지정
    USERNAME_FIELD = 'email'
 
    # 필수로 값을 받아야하는 필드 지정.
    REQUIRED_FIELDS = ['username', 'gender', 'phone']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh token" : str(refresh),
            "access token" : str(refresh.access_token)
        }

# Reference
# https://axce.tistory.com/m/99