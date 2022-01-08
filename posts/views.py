from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from posts.serializers import PostViewSerializer
from posts.models import Post
from accounts.models import User
# Create your views here.

class PostUploadViewAPI(GenericAPIView):

    queryset = User.objects.all()
    serializer_class = PostViewSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        
        image = request.FILES['image']

        request_user = self.queryset.filter(username=request.user.username).first()

        posting = Post.objects.create(
            title = serializer.validated_data['title'],
            user = request_user,
            image = image,
            description = serializer.validated_data['description']
        )
        
        posting.save()

        return Response(status=status.HTTP_200_OK)