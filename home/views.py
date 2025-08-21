from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper
from collections import defaultdict
from datetime import timedelta
from users.models import UserPreference
from stores.models import Store, Category
from visit_rewards.models import Visit
from ai_services.services import store_recommend
from accounts.models import UserLocation
from missions.models import DailyMissionRanking

def main(request):
    """
    홈 화면 뷰
    - 사용자 위치 기반 필터링
    - top_visits, review_best, AI 추천, 인기 챌린지
    """
    user_location = None
    gu_name = None

    if request.user.is_authenticated:
        user_location = UserLocation.objects.filter(user=request.user).first()
        gu_name = user_location.gu_name if user_location else None

    # ===============================
    # 1. 가게 필터링 (사용자 위치 기준)
    # ===============================
    stores_qs = Store.objects.all()
    if gu_name:
        stores_qs = stores_qs.filter(gu_name=gu_name)

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
    }

    return render(request, "home/main.html", context)
