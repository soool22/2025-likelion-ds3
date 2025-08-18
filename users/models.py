from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import os
from uuid import uuid4
from django.utils import timezone
from django.conf import settings



def upload_filepath(instance, filename):
    today_str = timezone.now().strftime("%Y%m%d")
    file_basename = os.path.basename(filename)
    return f'{instance._meta.model_name}/{today_str}/{uuid4().hex}_{file_basename}'

class User(AbstractUser):
    email = models.EmailField(max_length=30, unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    profile_image = models.ImageField(upload_to=upload_filepath, blank=True)
    
    points = models.PositiveIntegerField(default=0)

    groups = models.ManyToManyField(Group, related_name='users_custom', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='users_custom', blank=True)

    def __str__(self):
        return self.username


from stores.models import Store

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preference')
    preferred_food = models.CharField(max_length=50, blank=True, null=True)
    preferred_location = models.CharField(max_length=100, blank=True, null=True)

class FavoriteStore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store')
