from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import os
from uuid import uuid4
from django.utils import timezone

def upload_filepath(instance, filename):
    today_str = timezone.now().strftime("%Y%m%d")
    file_basename = os.path.basename(filename)
    return f'{instance._meta.model_name}/{today_str}/{uuid4().hex}_{file_basename}'

class User(AbstractUser):
    email = models.EmailField(max_length=30, unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    profile_image = models.ImageField(upload_to=upload_filepath, blank=True)

    groups = models.ManyToManyField(Group, related_name='users_custom', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='users_custom', blank=True)

    def __str__(self):
        return self.username
