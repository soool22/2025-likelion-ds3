import os
import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from visit_rewards.models import Gifticon
from django.conf import settings

gifticons_data = [
    ("기분좋은음식들", "기분좋은.png"),
    ("반숙상회", "반숙상회.png"),
    ("블랙다운", "블랙다운.png"),
    ("양국", "양국.png"),
    ("이요", "이요.png"),
    ("조이키친", "조이키친.png"),
    ("카페레", "카페레.png"),
    ("커피공장", "커피공장.png"),
]

for name, filename in gifticons_data:
    filepath = os.path.join(settings.MEDIA_ROOT, "gifticons", filename)
    if not os.path.exists(filepath):
        print(f"파일이 존재하지 않음: {filepath}")
        continue

    with open(filepath, "rb") as f:
        gifticon_file = File(f, name=filename)
        Gifticon.objects.create(
            name=name,
            point_cost=1000,
            description=f"{name} 기프티콘",
            image=gifticon_file
        )
    print(f"{name} 기프티콘 등록 완료")

print("모든 기프티콘 등록 완료")
