from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

def generate_coupon_code():
    return uuid.uuid4().hex[:10]

class Coupon(models.Model):
    COUPON_TYPES = [
        ('amount', '금액 할인'),
        ('percent', '비율 할인'),
        ('gift', '증정 이벤트'),
        ('custom', '직접 입력'),
    ]

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='coupons')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, default=generate_coupon_code)
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPES, default='amount')

    # 타입별 필드
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.FloatField(null=True, blank=True)
    gift_item = models.CharField(max_length=100, null=True, blank=True)
    custom_text = models.TextField(null=True, blank=True)

    expire_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.store.name} - {self.name}"
    
    

class UserCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self):
        self.used = True
        self.used_at = timezone.now()
        self.save()

# 쿠폰 발급 시 자동 배포
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_save, sender=Coupon)
def assign_coupon_to_users(sender, instance, created, **kwargs):
    if created:
        # 만료되지 않은 쿠폰만 발급
        if instance.expire_at is None or instance.expire_at > timezone.now():
            UserModel = get_user_model()
            users = UserModel.objects.all()

            # bulk_create로 효율화
            bulk_list = [
                UserCoupon(user=user, coupon=instance)
                for user in users
            ]
            UserCoupon.objects.bulk_create(bulk_list)
