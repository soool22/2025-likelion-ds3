import uuid
from django.db import models
from django.conf import settings
from stores.models import Store


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
# 교환 가능한 리워드
# -----------------------------
class Reward(models.Model):
    REWARD_TYPE_CHOICES = [
        ('gifticon', 'Gifticon'),
        ('discount', 'Discount'),
        ('item', 'Item'),
    ]

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='available_rewards', null=True, blank=True
    )
    name = models.CharField(max_length=100)  # 리워드 이름 (예: 아메리카노, 10% 할인권)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    cost_points = models.PositiveIntegerField(default=0)  # 교환에 필요한 포인트
    image = models.ImageField(upload_to="rewards/", blank=True, null=True)  # 가상의 기프티콘 이미지
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.cost_points} pts)"


# -----------------------------
# 유저가 실제로 교환한 리워드
# -----------------------------
class UserReward(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_rewards'
    )
    reward = models.ForeignKey(
        Reward, on_delete=models.CASCADE, related_name='claimed_rewards'
    )
    code = models.CharField(max_length=255, unique=True, default=uuid.uuid4)  # 발급 코드
    issued_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.reward.name} - {self.user.username} ({'사용됨' if self.used else '미사용'})"
