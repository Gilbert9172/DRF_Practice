#-- Django
from codecs import lookup
from django.db.models import query
from django.http.request import validate_host
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

#-- DRF
from rest_framework import generics, renderers, serializers, status, mixins, views
from rest_framework import response
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

#-- Module
from .models import User
from .serializers import (
    RegisterSerializer,EmailVerificationSerializer,
    LoginSerializer, ChangePasswordSerializer
)
from .utils import Util
from dotenv import load_dotenv
import os
from .renderer import UserRenderer

#-- JWT
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

#-- yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi





"""****************************************** Generic / Mixins 상속 ******************************************"""
"""
ListCreateAPIView는 mixins.ListModelMixin과 
mixins.CreateModelMixin 기능을 포함하고 있다. 

mixins를 상속 받을 경우 MRO에 따라, 
mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView 순으로
상속을 받아야한다. 
"""
#-- RegisterView (CVB)
# class RegisterView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer

    
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)



"""************************************************* APIView 상속 *************************************************"""
class RegisterView(GenericAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

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
        # https://django-rest-framework-simplejwt.readthedocs.io/en/latest/rest_framework_simplejwt.html?highlight=Refreschtoken.for_user()#rest_framework_simplejwt.tokens.Token.for_user
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




"""*************************************** RegisterView를 함수기반으로 작성 ***************************************"""
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



#-- is_verified를 True로 바꿔주는 로직.

"""*************************************** RegisterView를 함수기반으로 작성 ***************************************"""
# https://ctsictai.medium.com/drf-yasg-api-%EB%AC%B8%EC%84%9C-%EC%9E%90%EB%8F%99%ED%99%94-%EC%9E%91%EC%84%B1-part-2-68cacb14df34
class VerifyEmail(GenericAPIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter(
        'token',
        in_=openapi.IN_QUERY, 
        description='Bearer token',
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):

        token = request.GET.get('token')

        try:
            load_dotenv()
            token_decoding = jwt.decode(token, os.getenv('SECRET_KEY'), 'HS256')
            """
            decode알고리즘을 정의해줘야한다...

            payload 출력 결과
            {'token_type': 'access', 'exp': 1640763234, 'iat': 1640762334, 'jti': '37edb32aebc249a3a4e5102e42708d2d', 'user_id': 19}
            """
            user = User.objects.get(id=token_decoding['user_id'])
            if not user.is_verified :
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


"""*************************************** LoginAPIView ***************************************"""
import json

class LoginAPIView(GenericAPIView):
    queryset = None
    serializer_class = LoginSerializer
    
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        # breakpoint()
        serializer.is_valid(raise_exception=True)
        # json = JSONRenderer().render(serializer.data)
        # print(f'json 값: {json}')
        # print(f'json 값: {serializer.data}')
        # print(json==serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

#-- 비밀번호 수정.
class UpdatePassword(GenericAPIView):

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    lookup_field = 'id'
    
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data={"password" : request.data['password']}, partial=True)
        serializer.is_valid(raise_exception=True) # 여기까진 비번 안변함 (DB / serializer.data)
        self.perform_update(serializer) # 여기가 실행되면 DB에서 비번변경.(모델 인스턴스 생성)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    
#-- 아이디 찾기.
class FindIDView(RetrieveAPIView):
    pass