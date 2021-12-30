from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.contrib import auth

#-- RegisterSerializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )
    
    # 에러메세지 : create_user() got an unexpected keyword argument 'phone'
    # https://stackoverflow.com/questions/6007556/django-registration-create-user-unexpected-keyword
    # /accounts/managers.py를 수정해줌으로 해결.
    class Meta:
        model = User
        fields = ['email', 'username','gender' ,'phone', 'password'] 

    # https://brownbears.tistory.com/71
    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username','')
        """
        attrs 출력값.
        - 
        OrderedDict([('email', 'test@test.com'), ('username', '길준정1234'), ('gender', 'M'), ('phone', '010-4434-5325'), ('password', 'gilbert')])
        """
        if not email:
            raise serializers.ValidationError(self.default_error_messages)
        # .isalum() 문자열이 영어, 한글 혹은 숫자로 되어있으면 참 리턴, 아니면 거짓 리턴.
        if not username.isalnum():
            raise serializers.ValidationError(self.default_error_messages)

        return super().validate(attrs)


    # view.py로직에서 인스턴스를 생성해준다.
    # https://www.django-rest-framework.org/api-guide/serializers/
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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
    token = serializers.CharField(max_length=68, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password','token']

    def validate(self, attrs):
        email = attrs.get('email', '')

        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user.is_active:
            raise AuthenticationFailed('Account Disable, contact admin')
        
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')

        return {
            "email" : user.email,
            "password" : user.password,
            "token" : user.tokens
        }