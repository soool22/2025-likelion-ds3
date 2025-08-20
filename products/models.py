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

    def __str__(self):
        return f"{self.name} ({self.store.name})"
