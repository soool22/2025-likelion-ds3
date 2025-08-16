from django.db import models
from django.conf import settings
from stores.models import Store
from django.utils import timezone
from datetime import timedelta

# 점주가 생성하는 미션
class Mission(models.Model):
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE, related_name='missions')
    title = models.CharField(max_length=100)
    description = models.TextField()
    reward_description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    # 활성 기간
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now() + timedelta(days=7))
    
    def __str__(self):
        return f"[{self.store.name}] {self.title}"
    
    # 현재 활성 여부 자동 계산
    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

# 소비자가 미션을 완료했을 때
class MissionComplete(models.Model):
    mission = models.ForeignKey(to=Mission, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.mission.title} ({self.completed_at})"
