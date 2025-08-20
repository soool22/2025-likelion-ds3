from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper
from collections import defaultdict
from datetime import timedelta
from users.models import UserPreference
from stores.models import Store, Category
from visit_rewards.models import Visit
from ai_services.services import store_recommend  # AI 추천 가게

def main(request):
    # 1. 방문자 랭킹 상위 5개
    today = timezone.localdate()
    stores = Store.objects.all()
    
    # 누적 방문 + 오늘 방문
    visit_counts = defaultdict(int)
    visits = Visit.objects.all()
    for v in visits:
        key = v.store_id
        visit_counts[key] += 1

    for store in stores:
        store.visit_score = visit_counts.get(store.id, 0)
    
    top_visits = sorted(stores, key=lambda s: (-s.visit_score, -s.id))[:5]

    # 2. 리뷰 베스트 상위 5개
    a, b = 0.7, 0.3
    review_best = Store.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).annotate(
        score=ExpressionWrapper(
            (F('avg_rating') * a) + (F('review_count') * b),
            output_field=FloatField()
        )
    ).order_by('-score', '-id')[:5]

    # 3. AI 추천 가게 5개
    if request.user.is_authenticated:
        preference, _ = UserPreference.objects.get_or_create(user=request.user)
        if not preference.last_ai_recommendation or not preference.last_ai_call_time or \
           timezone.now() - preference.last_ai_call_time >= timedelta(minutes=1):
            recommended_stores = store_recommend(request.user)
        else:
            recommended_stores = preference.last_ai_recommendation
    else:
        recommended_stores = []

    categories = Category.objects.all()
    

    return render(request, "home/main.html", {
        'top_visits': top_visits,
        'review_best': review_best,
        'recommended_stores': recommended_stores,
        'categories': categories,
    })
