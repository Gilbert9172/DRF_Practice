from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )
    """
    create_user() got an unexpected keyword argument 'phone'
    https://stackoverflow.com/questions/6007556/django-registration-create-user-unexpected-keyword
    usermanager를 수정해줌으로 해결.
    """
    class Meta:
        model = User
        fields = ['email', 'username','gender' ,'phone', 'password'] 

    # view.py로직에서 인스턴스를 생성해준다.
    # https://www.django-rest-framework.org/api-guide/serializers/
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


#--
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']