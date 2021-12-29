#-- Django
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

#-- DRF
from rest_framework import generics, serializers, status, mixins, views
from rest_framework import response
from rest_framework.response import Response
from rest_framework import generics

#-- Module
from .models import User
from .serializers import (
    RegisterSerializer,EmailVerificationSerializer
)
from .utils import Util
from dotenv import load_dotenv
import os
from django.conf import settings

#-- JWT
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

#-- yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




#-- RegisterView (CVB)
"""
ListCreateAPIView는 mixins.ListModelMixin과 
mixins.CreateModelMixin 기능을 포함하고 있다. 

mixins를 상속 받을 경우 MRO에 따라, 
mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView 순으로
상속을 받아야한다. 
"""

#******************************************** Generic / Mixins 상속 ********************************************#
# class RegisterView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer

    
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
#*****************************************************************************************************************#




#************************************************* APIView 상속 *************************************************#
class RegisterView(generics.GenericAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def get(self, request):
        serializers = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializers.data)


    def post(self,request):

        # 유효성 검증을 위해 data를 넘겨줌.
        serializer = self.serializer_class(data=request.data)
        """
        serializer 출력 결과.
        - data : QueryDict
        
        RegisterSerializer(data=<QueryDict: {
            'csrfmiddlewaretoken': ['GnZtJZWvGd4WlCzJJ5KAPbuEeWzcDwK1wPPraI2EpNVPFe3gPKgYp6hKqekeUaTH'],
            'email': ['qwert@gilbert.com'], 'username': ['qwerty1234'], 'password': ['gilbert']
            }>):
            email = EmailField(max_length=255, validators=[<UniqueValidator(queryset=User.objects.all())>])
            username = CharField(max_length=255, validators=[<UniqueValidator(queryset=User.objects.all())>])
            password = CharField(max_length=68, min_length=6, write_only=True)
        """
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 검증 완료된 (json)값을 가져옴.
        user_data = serializer.data

        # token 
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        
        current_site = get_current_site(request).domain # 127.0.0.1:8000
        relativeLink = reverse('email-verify') # /auth/email-verify/
        
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'Hi '+user.username + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'} 

        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)
#*****************************************************************************************************************#




#**************************************** RegisterView를 함수기반으로 작성 ****************************************#
# from rest_framework.decorators import api_view

# @api_view(['GET','POST'])
# def register(request):

#     if request.method == "GET":

#         q = RegisterSerializer(User.objects.all(), many=True)

#         return Response(q.data, status=200)

#     elif request.method == "POST":
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
    
#     return Response(serializer.data, status=404)
#*****************************************************************************************************************#

#-- is_verified를 True로 바꿔주는 로직.
load_dotenv()
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Bearer token', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):

        token = request.GET.get('token')

        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), 'HS256')
            """
            decode알고리즘을 정의해줘야한다...

            payload 출력 결과
            {'token_type': 'access', 'exp': 1640763234, 'iat': 1640762334, 'jti': '37edb32aebc249a3a4e5102e42708d2d', 'user_id': 19}
            """
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified :
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)