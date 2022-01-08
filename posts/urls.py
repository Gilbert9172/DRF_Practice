from django.urls import path
from posts.views import PostUploadViewAPI


urlpatterns = [
    path('', PostUploadViewAPI.as_view(), name="post" )
]