from django.db import models
from django.conf import settings
from stores.models import Store
from django.utils import timezone
from datetime import timedelta
from visit_rewards.models import Visit
from visit_rewards.models import Reward

# 챌린지 종류
class MissionType(models.Model):
    key = models.CharField(max_length=50, unique=True)   # 예) amount, visit_count
    name = models.CharField(max_length=100)              # 화면 표시용 (예: 누적 금액)
    description = models.TextField(blank=True) # 미션 종류 설명
    unit = models.CharField(max_length=10, default='') # 단위 설정

    def __str__(self):
        return self.name
    
# 점주가 생성하는 챌린지
class Mission(models.Model):
    REWARD_TYPE_CHOICES = [
        ('POINT', '포인트'),
        ('CUSTOM', '직접 입력 보상'),  # 예: 음료 쿠폰, 사은품 등
    ]

    store = models.ForeignKey(to=Store, on_delete=models.CASCADE, related_name='missions')
    mission_type = models.ForeignKey(to=MissionType, on_delete=models.CASCADE, related_name='missions')

    title = models.CharField(max_length=100)
    description = models.TextField()

    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES, default='POINT')
    reward_points = models.PositiveIntegerField(default=0)  # 포인트 지급일 경우 사용
    reward_description = models.CharField(max_length=200, blank=True)  # CUSTOM 보상일 때 사용
    
    created_at = models.DateTimeField(auto_now_add=True)

    target_value = models.PositiveIntegerField() # 목표치 (금액, 방문 횟수, 기간 등)

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
    
    # 진행률 표시
    def progress_percent_for(self, user):
        try:
            progress = self.progresses.get(user=user)
            if self.target_value == 0:
                return 0
            return min(100, int((progress.current_value / self.target_value) * 100))
        except MissionProgress.DoesNotExist:
            return 0

# 사용자별 챌린지 진행 상황
class MissionProgress(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='progresses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_progress')
    current_value = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    reward_given = models.BooleanField(default=False) # 보상 지급됐는지 확인 여부

    class Meta:
        unique_together = ('mission', 'user')

    @property
    def percent(self):
        #현재 유저 기준 진행률
        if self.mission.target_value == 0:
            return 0
        return min(100, int((self.current_value / self.mission.target_value) * 100))
    
    @property
    def remaining(self):
        #목표까지 남은 값
        return max(0, self.mission.target_value - self.current_value)


    def check_completion(self):
        if not self.is_completed and self.current_value >= self.mission.target_value:
            self.is_completed = True
            self.save()
            MissionComplete.objects.get_or_create(mission=self.mission, user=self.user)

            # Reward 지급 (POINT 타입)
            if not self.reward_given and self.mission.reward_type == 'POINT':
                Reward.objects.create(
                    user=self.user,
                    reward_type='point',
                    amount=self.mission.reward_points,
                    description=f"{self.mission.title} 완료 보상"
                )
                self.user.points += self.mission.reward_points
                self.user.save()
                self.reward_given = True
                self.save()

# 소비자가 챌린지를 완료했을 때
class MissionComplete(models.Model):
    mission = models.ForeignKey(to=Mission, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.mission.title} ({self.completed_at})"

# 오늘의 인기 챌린지
class DailyMissionRanking(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    date = models.DateField()  # 오늘 날짜
    participant_count = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("mission", "date")

# 방문 1회당 누적금액 입력 1회
class VisitAmountAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)  # 금액 입력 완료 여부
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store', 'visit')  