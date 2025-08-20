from ai_services.services import store_recommend
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from stores.models import Store
from accounts.models import UserLocation
from missions.models import DailyMissionRanking
from django.utils import timezone

# 메인 화면
def main(request):
    """
    추천 가게
    """
    recommended_stores = store_recommend(request.user)

    """
    해당 구의 가게(Store)만 보여줌
    """
    user_location = None
    gu_name = None

    if request.user.is_authenticated:
        try:
            user_location = UserLocation.objects.get(user=request.user)
            gu_name = user_location.gu_name
        except UserLocation.DoesNotExist:
            pass

    """
    오늘의 인기 챌린지
    """
    today = timezone.localdate()  # 오늘 날짜 

    if gu_name:
    # 오늘 인기 챌린지 가져오기 (구 필터링 포함)
        rankings = DailyMissionRanking.objects.filter(
            date=today,
            mission__store__gu_name=gu_name
        )
    else:
    # 위치 설정 안 했으면 빈 쿼리셋
        rankings = DailyMissionRanking.objects.none()
    
    rankings = rankings.select_related("mission", "mission__store").order_by("rank")[:3]
    
    context = {
        "user_location": user_location,
        "gu_name": gu_name,
        "rankings": rankings, 
        "recommended_stores":recommended_stores,
    }
    return render(request, "home/main.html", context)
