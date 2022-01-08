from django.db import models
from django.conf import settings

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=10, null=False)
    user = models.ForeignKey(
                               settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE
                            )
    
    image = models.ImageField(
                              upload_to = 'img',
    )
    description = models.TextField()
