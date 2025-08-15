import uuid
from django.db import models
from django.conf import settings


# -----------------------------
# 유틸 함수
# -----------------------------
def generate_uuid():
    return uuid.uuid4().hex


# -----------------------------
# 가게 정보
# -----------------------------
class Store(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_stores')
    address = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    qr_token = models.CharField(max_length=255, unique=True, default=generate_uuid)  # QR 코드용 토큰
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -----------------------------
# 방문 기록
# -----------------------------
class Visit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visits')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='visits')
    qr_token = models.CharField(max_length=255)             # QR 토큰 기록
    test = models.BooleanField(default=False)              # 테스트용 구분
    visit_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} visited {self.store.name} on {self.visit_time}"


# -----------------------------
# 포인트/스탬프/기프티콘 관리
# -----------------------------
class Reward(models.Model):
    REWARD_TYPE_CHOICES = [
        ('point', 'Point'),
        ('stamp', 'Stamp'),
        ('gifticon', 'Gifticon'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rewards')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='rewards', null=True, blank=True)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    amount = models.PositiveIntegerField(default=0)  # 포인트 수, 스탬프 개수 등
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reward_type} ({self.amount})"


# -----------------------------
# 기프티콘 발급 내역
# -----------------------------
class Gifticon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gifticons')
    name = models.CharField(max_length=255)  # 예: 메가커피 아메리카노
    code = models.CharField(max_length=255, unique=True)  # 실제 발급 코드
    issued_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.user.username} ({'사용됨' if self.used else '미사용'})"
