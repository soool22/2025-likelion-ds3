import uuid
from django.db import models
from django.conf import settings
from stores.models import Store
from django.utils import timezone


# -----------------------------
# 유틸 함수
# -----------------------------
def generate_uuid():
    return uuid.uuid4().hex


# -----------------------------
# 방문 기록
# -----------------------------
class Visit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visits'
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='visits'
    )
    qr_token = models.CharField(max_length=255)  # 방문 인증할 때 사용한 QR 토큰
    test = models.BooleanField(default=False)    # 테스트 여부
    visit_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} visited {self.store.name} on {self.visit_time}"


# -----------------------------
# 캐릭터 꾸미기 아이템
# -----------------------------
class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ('decoration', 'Decoration'),
        ('accessory', 'Accessory'),
    ]

    name = models.CharField(max_length=50)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    point_cost = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    def __str__(self):
        return self.name

# -----------------------------
# 기프티콘
# -----------------------------
class Gifticon(models.Model):
    name = models.CharField(max_length=50)
    point_cost = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gifticons/', blank=True, null=True)

    def __str__(self):
        return self.name

# -----------------------------
# 유저 리워드
# -----------------------------
class Reward(models.Model):
    REWARD_TYPE_CHOICES = [
        ('point', 'Point'),
        ('item', 'Item'),
        ('gifticon', 'Gifticon'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES, default='point')
    related_visit = models.ForeignKey(Visit, null=True, blank=True, on_delete=models.SET_NULL)
    related_review = models.ForeignKey('reviews.Review', null=True, blank=True, on_delete=models.SET_NULL)  # 추가
    amount = models.PositiveIntegerField(default=0)  # 포인트
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    gifticon = models.ForeignKey(Gifticon, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        if self.item:
            return f"{self.user.username} - {self.item.name}"
        if self.gifticon:
            return f"{self.user.username} - {self.gifticon.name}"
        return f"{self.user.username} - {self.reward_type} - {self.amount}"

    
class PurchaseHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    gifticon = models.ForeignKey(Gifticon, on_delete=models.SET_NULL, null=True, blank=True)
    points_spent = models.PositiveIntegerField(default=0)
    purchased_at = models.DateTimeField(auto_now_add=True)