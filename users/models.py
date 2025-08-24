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
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 카테고리 (한식, 중식 등)
    preferred_categories = models.JSONField(default=list, blank=True)

    # 선호 맛 (매운맛, 단맛, 고소한맛 등)
    preferred_tastes = models.JSONField(default=list, blank=True)

    # 가격대 (저가, 중가, 고가 등)
    preferred_price_ranges = models.JSONField(default=list, blank=True)

    # 건강 요소 (저염식, 채식, 고단백 등)
    preferred_health = models.JSONField(default=list, blank=True)
    
    # 캐싱용 필드 추가
    last_ai_recommendation = models.JSONField(default=list, blank=True)
    last_ai_call_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}의 선호도"

class FavoriteStore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store')
        
