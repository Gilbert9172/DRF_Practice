from rest_framework import serializers, validators
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.contrib import auth
from django.core.validators import RegexValidator, MinLengthValidator

#-- RegisterSerializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True,
        validators=[MinLengthValidator(7, message="최소 7자리로 설정해주세요.")]
    )
    phone = serializers.CharField(
        max_length=13, validators=[RegexValidator(r"^010\d{4}\d{4}$", message=" '-' 빼고 11자리 입력해주세요")]
    )
    
    # 에러메세지 : create_user() got an unexpected keyword argument 'phone'
    # https://stackoverflow.com/questions/6007556/django-registration-create-user-unexpected-keyword
    # /accounts/managers.py를 수정해줌으로 해결.
    class Meta:
        model = User
        fields = ['email', 'username','gender' ,'phone', 'password'] 

    # https://brownbears.tistory.com/71
    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    #     username = attrs.get('username','')
    #     """
    #     attrs 출력값.
    #     - 
    #     OrderedDict([('email', 'test@test.com'), ('username', '길준정1234'), ('gender', 'M'), ('phone', '010-4434-5325'), ('password', 'gilbert')])
    #     """
    #     if not email:
    #         raise serializers.ValidationError(self.default_error_messages)
    #     # .isalum() 문자열이 영어, 한글 혹은 숫자로 되어있으면 참 리턴, 아니면 거짓 리턴.
    #     if not username.isalnum():
    #         raise serializers.ValidationError(self.default_error_messages)

    #     return attrs


    # # view.py로직에서 인스턴스를 생성해준다.
    # # https://www.django-rest-framework.org/api-guide/serializers/
    # def create(self, validated_data):
    #     return User.objects.create_user(**validated_data)


#-- EmailVerificationSerializer
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


#-- LoginSerializer
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=3, write_only=True)
    access_token = serializers.CharField(max_length=68, read_only=True)
    refresh_token = serializers.CharField(max_length=68, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password','access_token', 'refresh_token']

    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    
    #     password = attrs.get('password', '')
        
    #     user = auth.authenticate(email=email, password=password)
        
    #     if not user.is_active:
    #         raise AuthenticationFailed('Account Disable, contact admin')
        
    #     if not user.is_verified:
    #         raise AuthenticationFailed('Email is not verified')
        
    #     if not user:
    #         raise AuthenticationFailed('Invalid credentials, try again')

    #     return {
    #         "email" : user.email,
    #         "password" : user.password,
    #         "access_token" : user.tokens()['access token'],
    #         "refresh_token" : user.tokens()['refresh token']  
    #     }
        
class ChangePasswordSerializer(serializers.ModelSerializer):

    email = serializers.CharField(max_length=30)

    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True,
        validators=[MinLengthValidator(7, message="최소 7자리로 설정해주세요.")]
    )
    new_password = serializers.CharField(
        max_length=68, min_length=6, write_only=True,
        validators=[MinLengthValidator(7, message="최소 7자리로 설정해주세요.")]
    )
    check_password = serializers.CharField(
        max_length=68, min_length=6, write_only=True,
        validators=[MinLengthValidator(7, message="최소 7자리로 설정해주세요.")]
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'new_password', 'check_password']

    # #-- validation
    # def validate_password(self, value):
    #     if not value:
    #         raise serializers.ValidationError

    # def update(self, instance, validated_data):
    #     # breakpoint()
    #     # instance.password = validated_data.get('password') # 이렇게 하면 비밀번호가 그대로 넘어감.
    #     instance.set_password(validated_data['password'])
    #     instance.save()
    #     return instance


class UserDetailSerializer(serializers.ModelSerializer):
    # userName = serializers.CharField(source='username')
    class Meta:
        model = User
        fields = ['username']

class EmailFindSerializer(serializers.ModelSerializer):

    username = serializers.CharField(max_length=10)
    password = serializers.CharField(max_length=68, min_length=3, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']