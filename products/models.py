from django.db import models
from django.conf import settings
from stores.models import Store
from uuid import uuid4
from django.utils import timezone
import os

def upload_filepath(instance,filename):
    today_str = timezone.now().strftime("%Y%m%d")
    file_basename = os.path.basename(filename)
    return f'product/{today_str}/{str(uuid4())}_{file_basename}'

# 상품/메뉴 
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)  # 상품명
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격
    image = models.ImageField(upload_to=upload_filepath, null=True, blank=True)  # 상품 이미지
    description = models.TextField(blank=True)  # 상품 설명
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_main = models.BooleanField(default=False) # 대표 메뉴 여부

    def save(self, *args, **kwargs):
        if self.is_main:
            # 같은 가게의 다른 대표 메뉴를 False로 변경
            Product.objects.filter(store=self.store, is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} ({self.store.name})"
