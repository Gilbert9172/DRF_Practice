from rest_framework import serializers
from posts.models import Post

class PostViewSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Post
        fields = ['title', 'image', 'description']

    