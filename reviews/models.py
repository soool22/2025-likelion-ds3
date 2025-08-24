from django.db import models
from django.conf import settings
from stores.models import Store
import os
from uuid import uuid4
from django.utils import timezone

# 리뷰 이미지 업로드 경로 설정
def upload_filepath(instance, filename):
    today_str = timezone.now().strftime("%Y%m%d")
    file_basename = os.path.basename(filename)
    return f'{instance._meta.model_name}/{today_str}/{str(uuid4())}_{file_basename}'

# 리뷰 모델
class Review(models.Model):
    store = models.ForeignKey(Store, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1~5점 평점
    comment = models.TextField(max_length=300, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # 좋아요
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reviews', blank=True)

    def __str__(self):
        return f"{self.user} - {self.store.name} ({self.rating}점)"

    @property
    def like_count(self):
        return self.likes.count()
    
# 리뷰 이미지 모델 (다중 이미지)
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_filepath, blank=True, null=True)
