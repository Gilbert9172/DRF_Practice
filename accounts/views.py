#-- Django
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth
from django.core.cache import cache

#-- DRF
from rest_framework import generics, renderers, serializers, status, mixins, views
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

#-- Module
from .models import User
from .serializers import (
    RegisterSerializer,EmailVerificationSerializer,
    LoginSerializer, ChangePasswordSerializer,
    UserDetailSerializer, EmailFindSerializer
)
from .utils import Util, Encrypt
from dotenv import load_dotenv
import os
from .renderer import UserRenderer
from expenses.permissions import IsOwner, OnlyOwner
# from drf_todo.settings import CACHE_TTL

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
    """
        get:
            회원 정보 조회


        ---

        post:
            회원가입

        ---

        # Request Params

            [ Body:json ]

                - email     : 이메일
                - username  : 아이디
                - gender    : 성별
                - phone     : 전화번호
                - password  : 비밀번호

        ---

        # Response Params

            [Body:json]

                - response
                        ㄴ{
                            message : 성공 or 에러메세지 
                          }
        ---
    """

    # def post(self,request):

    #     # 유효성 검증을 위해 data를 넘겨줌.
    #     serializer = self.serializer_class(data=request.data)
    #     """
    #     serializer 출력 결과.
    #     - data : QueryDict
        
    #     RegisterSerializer(data=<QueryDict: {
    #         'csrfmiddlewaretoken': ['GnZtJZWvGd4WlCzJJ5KAPbuEeWzcDwK1wPPraI2EpNVPFe3gPKgYp6hKqekeUaTH'],
    #         'email': ['qwert@gilbert.com'], 'username': ['qwerty1234'], 'password': ['gilbert']
    #         }>):
    #         email = EmailField(max_length=255, validators=[<UniqueValidator(queryset=User.objects.all())>])
    #         username = CharField(max_length=255, validators=[<UniqueValidator(queryset=User.objects.all())>])
    #         password = CharField(max_length=68, min_length=6, write_only=True)
    #     """
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     # 검증 완료된 (json)값을 가져옴.
    #     user_data = serializer.data

    #     # token 
    #     user = User.objects.get(email=user_data['email'])
    #     # https://django-rest-framework-simplejwt.readthedocs.io/en/latest/rest_framework_simplejwt.html?highlight=Refreschtoken.for_user()#rest_framework_simplejwt.tokens.Token.for_user
    #     token = RefreshToken.for_user(user).access_token
        
    #     current_site = get_current_site(request).domain # 127.0.0.1:8000
    #     relativeLink = reverse('email-verify') # /auth/email-verify/
        
    #     absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
    #     email_body = 'Hi '+user.username + \
    #         ' Use the link below to verify your email \n' + absurl
    #     data = {'email_body': email_body, 'to_email': user.email,
    #             'email_subject': 'Verify your email'} 

    #     Util.send_email(data)

    #     return Response(user_data, status=status.HTTP_201_CREATED)
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request, *args, **kwargs): 
        
        # redis 캐시 설정
        # cache_username = [ i.username for i in self.get_queryset() ]
        # cache.set('all_username', cache_username, CACHE_TTL)

        # cache_email = [ i.email for i in self.get_queryset() ]
        # cache.set('all_email', cache_email, CACHE_TTL)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.data['username']
        email = serializer.data['email']
        gender = serializer.data['gender']
        phone = serializer.data['phone']
        password = serializer.validated_data['password']
    
        # all_username = cache.get('all_username')
        # all_email = cache.get('all_email')

        # username 확인
        check_user_q = self.queryset.filter(username=username).first()
        if check_user_q:
        
        # if username in all_username:
            response = {
                "message" : "Fail",
            } 

        # email 확인
        check_email_q = self.queryset.filter(email=email).first()
        if check_email_q:

        # if email in all_email:
            response = {
                "message" : "Fail",
            } 
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # user 객체 생성 / DB 저장
        user = User.objects.create_user(
            username = username,
            email = email,
            gender = gender,
            phone = phone,
        )

        user.set_password(password)
        user.save()
        
        return Response(data={"message":"success"}, status=status.HTTP_200_OK)


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
class LoginAPIView(GenericAPIView):
    """
        post: 
            회원 로그인

        ---

        # Request Params

            [ Body:json ]

                - email    : 사용자 이메일
                - password : 비밀번호 

        ---

        # Response Params

            [ Body:json ]

                - response 
                        ㄴ {
                                user_email          :  사용자 이메일
                                user_access_token   :  access 토큰
                                user_refresh_token  :  refresh 토큰             
                           }
                
        ---
    """
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    renderer_classes = [JSONRenderer]

    def post(self,request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)   # 값이 잘 들어갔는지 확인.
        
        user_email = serializer.data['email']
        user_password = serializer.validated_data['password']
        
        user = auth.authenticate(email=user_email, password=user_password)
        
        if not user:
            response = {
                "message" : "존재하지 않는 이메일"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        obj = {
            "user_email" : user_email,
            "user_access_token" : user.tokens()['access token'],
            "user_refresh_token" : user.tokens()['refresh token']
        }
        return Response({"response":obj}, status=status.HTTP_200_OK)       


#-- 비밀번호 변경 --#
class UpdatePassword(GenericAPIView):
    """
        patch:
            비밀번호 변경
        
        ---

        # Request Params

            [ Headers ]

                - Bearer Token : Bearer 토큰 값



            [ Body:json ]

                - email          : 사용자 이메일
                - password       : 기존 비밀번호
                - new_password   : 새로운 비밀번호 입력
                - check_password : 새로운 비밀번호 재입력

        ---

        # Response Params

            [ Body:json ]

                - response 
                        ㄴ{
                             message : 실패 메세지 or 성공 메세지             
                          }
        
        ---
    
    """
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChangePasswordSerializer
    # lookup_field = 'id'
    
    # def patch(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.serializer_class(instance, data={"password" : request.data['password']}, partial=True)
    #     serializer.is_valid(raise_exception=True) # 여기까진 비번 안변함 (DB / serializer.data)
    #     self.perform_update(serializer) # 여기가 실행되면 DB에서 비번변경.(모델 인스턴스 생성)
    #     return Response(serializer.data)

    # def perform_update(self, serializer):
    #     serializer.save()
    
    def patch(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # 사용자 확인
        user = auth.authenticate(email=email, password=password)
        if user == None:
            response = {
                "message" : "인증되지 않은 사용자"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호 일치 여부 확인
        new_password = serializer.validated_data['new_password']
        check_password = serializer.validated_data['check_password']

        if new_password != check_password:
            response = {
                "message" : "비밀번호가 다릅니다."
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        
        response = {
            "message" : "비밀번호 변경 성공"
        }
        return Response(response, status=status.HTTP_200_OK)
    
    
#-- 프로필 조회 --#
class UserDetailView(GenericAPIView):
    """
        get:
            회원 프로필 정보

        ---

        # Request Params

            [ Headers ]

                - Bearer Token : Bearer 토큰 값



            [ Params ]

                - username     : 사용자 아이디

        ---

        # Response Params

            [ Body ]

                - respones 
                        ㄴ {
                                username : 아이디
                                email    : 이메일
                                phone    : 전화번호
                                gender   : 성별
                           }
        ---
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,OnlyOwner)
    
    def get(self, request, *args, **kwargs):
        
        username = request.query_params.get('username')
        user_info_query = self.queryset.filter(username=username).first()

        if not user_info_query:
            return Response(status=status.HTTP_204_NO_CONTENT, data={"result":"No User"}) 

        user_q = {
            "username" : user_info_query.username,
            "email" : user_info_query.email,
            "phone" : user_info_query.phone,
            "gender" : user_info_query.gender,
        }

        return Response(user_q, status=status.HTTP_200_OK)


#-- 회원 이메일 찾기 --#
class EmailFindAPIView(GenericAPIView):
    """
        post:
            회원 이메일 찾기
    
    ---

    # Request Params

        [ Body:json ]

            - username  : 아이디
            - password  : 비밀번호
    
    ---

    # Response Params

        [ Body:json ]

            - response
                    ㄴ{
                         result  : Success / Fail
                         message : Error / Email 
                      }
    ---
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailFindSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.data['username']
        password = Encrypt().encrypt_str(serializer.validated_data['password'])
        

        user_q = self.get_queryset().filter(username=username).first()
        if not user_q:
            response = {
                "result" : "Fail",
                "message" : "등록되지 않은 정보"
            }

        db_pw = user_q.password
        if password != db_pw:
            response = {
                "result" : "Fail",
                "messgae" : "옳지 않은 비밀번호"
            }


        response = {
            "result" : "Success",
            "message" : user_q.email
        }

        return Response(response, status=status.HTTP_200_OK)