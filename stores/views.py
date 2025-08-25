from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper
from django.http import JsonResponse
from collections import defaultdict
from django.db import models
import datetime

from .models import Store, Category
from .forms import StoreForm
from .utils import haversine, get_user_location, annotate_distance, calculate_visit_counts, format_distance
from visit_rewards.models import Visit
from ai_services.services import summarize_reviews  # ai_services에서 요약 함수
from datetime import timedelta

from missions.models import VisitAmountAccess
from visit_rewards.models import Visit

from missions.utils import challenge_summary
from .utils import annotate_distance
################ 점주 ################

# 가게 등록
@login_required
def store_create(request):

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.latitude = request.POST.get('latitude')
            store.longitude = request.POST.get('longitude')
            store.owner = request.user
            store.save()
            # ManyToMany 카테고리 저장
            form.save_m2m()
            
            messages.success(request, '가게 등록 완료!')
            return redirect('stores:owner-store-list')
        else:
            messages.error(request, '입력 정보를 확인해주세요.')
    else:
        form = StoreForm()
    
    categories = Category.objects.all()
    return render(request, 'stores/store-create.html', {
        'form': form,
        'categories': categories
    })

# 가게 위도/경도 정보
def store_location(request):
    stores = Store.objects.all()
    data = []
    for store in stores:
        data.append({
            "id": store.id,
            "name": store.name,
            "latitude": store.latitude,
            "longitude": store.longitude,
            "rating": store.rating,
            "image_url": store.image.url if store.image else None,
        })
    return JsonResponse({"stores": data})

# 점주용: 내가 등록한 가게 목록
@login_required
def owner_store_list(request):
    stores = request.user.store_set.all()
    today = timezone.localdate()
    now = timezone.localtime()  # 현재 시간

    store_data = []

    for store in stores:
        # 오늘/누적 방문
        today_visits = store.visits.filter(visit_time__date=today).count()
        total_visits = store.visits.count()

        # 챌린지 통계 가져오기 (utils.py 함수 사용)
        challenge_stats = challenge_summary(store)

        # 운영 시간 체크
        if store.open_time and store.close_time:
            open_time_today = timezone.make_aware(
                datetime.datetime.combine(today, store.open_time)
            )
            close_time_today = timezone.make_aware(
                datetime.datetime.combine(today, store.close_time)
            )
            is_open = open_time_today <= now <= close_time_today
        else:
            is_open = False

        store_data.append({
            'store': store,
            'today_visits': today_visits,
            'total_visits': total_visits,
            'is_open': is_open,
            **challenge_stats,
        })

    return render(request, 'stores/owner-store-list.html', {
        'store_data': store_data,
        'now': now
    })

# 등록한 가게 삭제
@login_required
def store_delete(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == 'POST':
        store.delete()
        messages.success(request, '가게가 삭제되었습니다.')
        return redirect('stores:owner-store-list')

    # 삭제 확인 페이지
    return render(request, 'stores/store-delete.html', {'store': store})

# 등록한 가게 정보 수정
@login_required
def store_update(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, '가게 정보가 수정되었습니다.')
            return redirect('stores:owner-store-list')
        else:
            messages.error(request, '입력 정보를 확인해주세요.')
    else:
        form = StoreForm(instance=store)

    return render(request, 'stores/store-update.html', {
        'store': store,
        'form': form,
    })

# 셀프 서비스
def self_service(request,store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    
    is_open = False
    now = timezone.localtime()  # aware datetime

    if store.open_time and store.close_time:
        # 오늘 날짜와 시간 결합
        open_dt = datetime.datetime.combine(now.date(), store.open_time)
        close_dt = datetime.datetime.combine(now.date(), store.close_time)

        # aware datetime으로 변환
        open_dt = timezone.make_aware(open_dt, timezone.get_current_timezone())
        close_dt = timezone.make_aware(close_dt, timezone.get_current_timezone())

        if open_dt <= now <= close_dt:
            is_open = True

    return render(request, 'stores/self-service.html', {
        'store': store,
        'is_open': is_open
    })

# 가게 상세 페이지
def owner_store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = store.products.all()
    missions = store.missions.filter(end_date__gte=timezone.now())

    context = {
        'store': store,
        'products': products,
        'missions': missions,
        'ai_summary': store.review_summary_text,
        'review_keywords': store.review_keywords.split(",") if store.review_keywords else [],
        'snippet': store.review_snippet,
    }

    return render(request, 'stores/owner-store-detail.html', context)

################ 소비자용 ################

# 공통 필터 함수 (카테고리 + 지역구 + 거리)
def filter_stores(request, stores):
    category_slug = request.GET.get('category')
    gu = request.GET.get('gu')
    user_lat, user_lng, user_gu = get_user_location(request.user) if request.user.is_authenticated else (37.5665, 126.9780, "서울특별시")

    if category_slug:
        stores = stores.filter(category__slug=category_slug)
    if gu:
        stores = stores.filter(gu_name__icontains=gu)
    else:
        stores = stores.filter(gu_name__icontains=user_gu)

    stores = list(annotate_distance(stores, user_lat, user_lng))
    categories = Category.objects.all()

    return stores, categories, user_lat, user_lng, gu or user_gu, category_slug

# 모든 가게 목록
def public_store_list(request):
    stores = Store.objects.all().order_by('-id')
    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)
    
    for store in stores:
        if store.latitude and store.longitude:
            distance_m = haversine(user_lat, user_lng, store.latitude, store.longitude)
            store.distance_m = distance_m
            store.distance = format_distance(distance_m)
        else:
            store.distance_m = None
            store.distance = None

    return render(request, 'stores/public-store-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': selected_category,
        'selected_gu': selected_gu,
        'user_lat': user_lat,
        'user_lng': user_lng,
    })

# 인기 가게 (방문자 수)
def popular_store_list(request):
    # 사용자 위치
    if request.user.is_authenticated:
        user_lat, user_lng, _ = get_user_location(request.user)
    else:
        user_lat, user_lng = 37.5665, 126.9780  # 서울시청 기본값

    # 전체 Store 조회
    stores = Store.objects.all()

    # 거리 계산
    for store in stores:
        if store.latitude and store.longitude:
            distance_m = haversine(user_lat, user_lng, store.latitude, store.longitude)
            store.distance_m = distance_m
            store.distance = format_distance(distance_m)
        else:
            store.distance_m = None
            store.distance = None

    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)

    # 방문 수 계산: 모든 Visit 객체에서 store별 누적 방문수
    visit_counts = Visit.objects.values('store_id').annotate(count=models.Count('id'))
    visit_count_dict = {vc['store_id']: vc['count'] for vc in visit_counts}

    # Store 객체에 visit_count 속성 추가
    for store in stores:
        store.visit_count = visit_count_dict.get(store.id, 0)

    # 방문 수 높은 순, 같은 방문수면 최신 등록 순
    stores = sorted(stores, key=lambda s: (-s.visit_count, -s.id))

    categories = Category.objects.all()

    return render(request, 'stores/popular-store-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': selected_category,
        'selected_gu': selected_gu,
        'user_lat': user_lat,
        'user_lng': user_lng,
    })

# 리뷰 Best
def review_best_list(request):
    # 사용자 위치
    if request.user.is_authenticated:
        user_lat, user_lng, _ = get_user_location(request.user)
    else:
        user_lat, user_lng = 37.5665, 126.9780  # 서울시청 기본값

    # 전체 Store 조회
    stores = Store.objects.all()

    # 거리 계산
    for store in stores:
        if store.latitude and store.longitude:
            distance_m = haversine(user_lat, user_lng, store.latitude, store.longitude)
            store.distance_m = distance_m
            store.distance = format_distance(distance_m)
        else:
            store.distance_m = None
            store.distance = None
            
    a, b = 0.7, 0.3
    category_slug = request.GET.get('category')
    gu = request.GET.get('gu')
    user_lat, user_lng, user_gu = get_user_location(request.user) if request.user.is_authenticated else (37.5665, 126.9780, "서울특별시")

    stores = Store.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).annotate(
        score=ExpressionWrapper((F('avg_rating')*a)+(F('review_count')*b), output_field=FloatField())
    ).order_by('-score', '-id')

    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)

    return render(request, 'stores/review-best-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': selected_category,
        'selected_gu': selected_gu,
        'user_lat': user_lat,
        'user_lng': user_lng,
    })

# 가게 검색
@login_required
def store_search(request):
    
    
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    category_slug = request.GET.get('category')
    
    stores = Store.objects.all().order_by('-id')

    # 사용자 위치
    user_lat, user_lng, gu_name= get_user_location(request.user) if request.user.is_authenticated else (37.5665, 126.9780)
    
    # 지역구 기준 필터링
    stores = Store.objects.all().order_by('-id')
    if gu_name:
        stores = stores.filter(gu_name=gu_name)
    
    if query:
        stores = stores.filter(name__icontains=query)
    
    if category_slug:
        stores = stores.filter(category__slug=category_slug)

    # 거리 계산 (상세 페이지처럼 직접 처리)
    for store in stores:
        if store.latitude and store.longitude:
            distance_m = haversine(user_lat, user_lng, store.latitude, store.longitude)
            store.distance_m = distance_m        # 계산용 숫자
            store.distance = format_distance(distance_m)  # 출력용 문자열
        else:
            store.distance_m = None
            store.distance = None
    
    # 정렬
    if sort == "rating":
        stores = sorted(stores, key=lambda s: (-s.rating, s.id))
    elif sort == "visit":
        visit_counts = {v['store_id']: v['count'] for v in Visit.objects.values('store_id').annotate(count=Count('id'))}
        for s in stores:
            s.visit_count = visit_counts.get(s.id, 0)
        stores = sorted(stores, key=lambda s: (-getattr(s, 'visit_count', 0), s.id))
    elif sort == "distance":
        stores = sorted(stores, key=lambda s: s.distance_m if s.distance_m is not None else float('inf'))

    categories = Category.objects.all()
    
    return render(request, "stores/store-search.html", {
        "stores": stores,
        "categories": categories,
        "query": query or "",
        "selected_category": category_slug,
        "user_lat": user_lat,
        "user_lng": user_lng,
        "sort": sort,
    })



# 가게 상세 페이지
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = store.products.all()
    missions = store.missions.filter(end_date__gte=timezone.now())

    # 사용자 위치 가져오기
    if request.user.is_authenticated:
        user_lat, user_lng, _ = get_user_location(request.user)
    else:
        user_lat, user_lng = 37.5665, 126.9780  # 서울시청

    # 거리 계산 (annotate_distance 활용)
    if store.latitude and store.longitude:
        distance_m = haversine(user_lat, user_lng, store.latitude, store.longitude)
        store.distance_m = distance_m           # 숫자(m)
        store.distance = format_distance(distance_m)  # 문자열(km/m)
    else:
        store.distance_m = None
        store.distance = None

    # 마지막 요약 갱신 30분 이상 지났으면 새로 호출
    if not store.review_summary_updated or timezone.now() - store.review_summary_updated > timedelta(minutes=30):
        store = summarize_reviews(store)

    # 즐겨찾기 여부
    is_favorite = request.user.is_authenticated and request.user.favorites.filter(id=store.id).exists()

    # 최근 방문 기록
    time_threshold = timezone.now() - timedelta(hours=24)
    recent_visit = Visit.objects.filter(user=request.user, store=store, visit_time__gte=time_threshold).order_by('-visit_time').first()

    user_can_access_amount = False
    if recent_visit:
        access_record = VisitAmountAccess.objects.filter(user=request.user, store=store, visit=recent_visit).first()
        if not access_record or not access_record.used:
            user_can_access_amount = True

    context = {
        'store': store,
        'products': products,
        'missions': missions,
        'ai_summary': store.review_summary_text,
        'review_keywords': store.review_keywords.split(",") if store.review_keywords else [],
        'snippet': store.review_snippet,
        'is_favorite': is_favorite,
        'user_can_access_amount': user_can_access_amount,
        'user_lat': user_lat,
        'user_lng': user_lng,
    }

    return render(request, 'stores/store-detail.html', context)

from visit_rewards.utils import generate_store_qr

#QR발급
def owner_qr(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # QR 코드 생성
    store_qr_file, qr_url = generate_store_qr(store, host=request.get_host(), test=False)

    # base64 변환
    import base64
    from io import BytesIO
    buffer = BytesIO()
    store_qr_file.open()  # File 객체 열기
    buffer.write(store_qr_file.read())
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    store_qr_url = f"data:image/png;base64,{qr_base64}"

    return render(request, 'stores/owner-qr.html', {
        'store': store,
        'store_qr_url': store_qr_url,
        'qr_url': qr_url,  # 필요하면 JS fetch용
    })