from django.db import models
from django.conf import settings
import os
import uuid
from uuid import uuid4
from django.utils import timezone

# 가게 이미지 업로드
def upload_filepath(instance,filename):
    today_str=timezone.now().strftime("%Y%m%d")
    file_basename=os.path.basename(filename)
    return f'{instance._meta.model_name}/{today_str}/{str(uuid4())}_{file_basename}'

# 가게 카테고리 ( ex) 음식점, 카페 등등)
class Category(models.Model):
    name=models.CharField(max_length=50,unique=True)
    slug=models.SlugField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
    import uuid

def generate_uuid():
    return uuid.uuid4().hex

    
# 가게
class Store(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False) # 가게 이름
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 점주 계정 ( 현재 로그인한 모든 계정 포함 )
    address = models.CharField(max_length=255, null=False, blank=False) # 주소
    #latitude = models.FloatField(null=False) # 위도
    #longitude = models.FloatField(null=False) # 경도
    
    qr_token = models.CharField(max_length=255, unique=True, default=generate_uuid)

    
    category = models.ManyToManyField(Category, related_name="stores") # 카테고리
    rating = models.FloatField(default=0) # 평균 평점
    visit_count = models.IntegerField(default=0) # 방문 수
    image = models.ImageField(upload_to='upload_filepath', blank=True)

    description = models.TextField(blank=True) # 챌린지 설명
    secret_code = models.CharField(max_length=10, blank=False, null=False)  # 점주 코드(누적 금액)

    # 영업 시간
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    # 현재 영업 중인지 확인
    @property
    def is_open(self):
        if self.open_time and self.close_time:
            now = timezone.localtime().time()
            # 오픈 시간과 종료 시간 사이면 True
            return self.open_time <= now <= self.close_time
        return False
    
    # 평균 평점 매기기
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            self.rating = sum(r.rating for r in reviews) / reviews.count()
        else:
            self.rating = 0
        self.save()

    def __str__(self):
        return self.name

