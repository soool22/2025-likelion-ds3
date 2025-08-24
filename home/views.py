from django.shortcuts import render
from django.utils import timezone
from collections import defaultdict
from datetime import timedelta
from stores.models import Store, Category
from visit_rewards.models import Visit
from users.models import UserPreference
from ai_services.services import store_recommend
from stores.utils import annotate_distance, get_user_location
from missions.models import DailyMissionRanking
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper

def main(request):
    user_location = None
    gu_name = None
    user_lat, user_lng = 37.5665, 126.9780  # 기본값 서울시청

    if request.user.is_authenticated:
        try:
            user_lat, user_lng, gu_name = get_user_location(request.user)
            if gu_name:
                user_location = {'gu_name': gu_name}
        except:
            user_location = None

    # ===============================
    # 1. 가게 필터링 (사용자 위치 기준)
    # ===============================
    stores_qs = Store.objects.all()
    if gu_name:
        stores_qs = stores_qs.filter(gu_name=gu_name)

    # 거리 계산
    stores_qs = annotate_distance(stores_qs, user_lat, user_lng)

    # ===============================
    # 2. 방문자 랭킹 top 5
    # ===============================
    visit_counts = defaultdict(int)
    for v in Visit.objects.select_related('store').all():
        if gu_name and v.store.gu_name != gu_name:
            continue
        visit_counts[v.store_id] += 1

    top_visits = sorted(
        [store for store in stores_qs],
        key=lambda s: (-visit_counts.get(s.id, 0), -s.id)
    )[:5]

    # ===============================
    # 3. 리뷰 베스트 top 5
    # ===============================
    a, b = 0.7, 0.3
    review_best = stores_qs.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).annotate(
        score=ExpressionWrapper(
            F('avg_rating') * a + F('review_count') * b,
            output_field=FloatField()
        )
    ).order_by('-score', '-id')[:5]

    # 거리 계산
    review_best = annotate_distance(review_best, user_lat, user_lng)


    # ===============================
    # 4. AI 추천 가게
    # ===============================
    recommended_stores = []
    if request.user.is_authenticated:
        preference, _ = UserPreference.objects.get_or_create(user=request.user)
        if not preference.last_ai_recommendation or not preference.last_ai_call_time or \
            timezone.now() - preference.last_ai_call_time >= timedelta(minutes=1):
            recommended_stores = store_recommend(request.user)
        else:
            recommended_stores = preference.last_ai_recommendation

        # DB에서 Store 객체로 가져오기 + 지역구 필터링 + 거리 계산
    recommended_stores_objs = []
    for s in recommended_stores:
        store_id = s["id"] if isinstance(s, dict) else s  # dict이면 id 꺼내고, int면 그대로 사용
        try:
            store_obj = Store.objects.get(id=store_id)
            # 지역구 필터링
            if gu_name and store_obj.gu_name != gu_name:
                continue
            recommended_stores_objs.append(store_obj)
        except Store.DoesNotExist:
            continue

    recommended_stores = annotate_distance(recommended_stores_objs, user_lat, user_lng)

    # ===============================
    # 5. 오늘의 인기 챌린지
    # ===============================
    rankings = DailyMissionRanking.objects.none()
    if gu_name:
        today = timezone.localdate()
        rankings = DailyMissionRanking.objects.filter(
            date=today,
            mission__store__gu_name=gu_name
        ).select_related("mission", "mission__store").order_by("rank")[:3]

    # ===============================
    # 6. 카테고리
    # ===============================
    categories = Category.objects.all()

    context = {
        'top_visits': top_visits,
        'review_best': review_best,
        'recommended_stores': recommended_stores,
        'categories': categories,
        'user_location': user_location,
        'gu_name': gu_name,
        'rankings': rankings,
        'user_lat': user_lat,
        'user_lng': user_lng,
    }

    return render(request, "home/main.html", context)

def alarm_center(request):
    
    return render(request, 'home/alarmcenter.html')