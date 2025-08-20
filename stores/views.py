from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper
from django.http import JsonResponse
from collections import defaultdict

from .models import Store, Category
from .forms import StoreForm
from .utils import haversine, get_user_location, annotate_distance, calculate_visit_counts
from visit_rewards.models import Visit

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
    stores = Store.objects.filter(owner=request.user).order_by('-id')
    return render(request, 'stores/owner-store-list.html', {'stores': stores})

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

################ 소비자용 ################

# 공통 필터 함수
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

    stores = annotate_distance(stores, user_lat, user_lng)
    categories = Category.objects.all()

    return stores, categories, user_lat, user_lng, gu or user_gu, category_slug

# 모든 가게 목록
def public_store_list(request):
    stores = Store.objects.all().order_by('-id')
    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)

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
    stores = Store.objects.all()
    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)

    today = timezone.localdate()
    visits_today = Visit.objects.filter(visit_time__date=today)
    stores = calculate_visit_counts(stores, visits_today, request.GET.get('category'))

    stores = sorted(stores, key=lambda s: (-getattr(s, 'visit_count', 0), -s.id))

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
    stores = Store.objects.all().order_by('-id')

    if query:
        stores = stores.filter(name__icontains=query)

    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)

    # 정렬
    if sort == "rating":
        # 기존 distance 값은 그대로 두고 평점 기준 정렬
        stores = sorted(stores, key=lambda s: (-s.rating, s.id))
    elif sort == "visit":
        # 방문자순: distance 유지
        # 먼저 visit_count 속성 계산
        visit_counts = {v['store_id']: v['count'] for v in Visit.objects.values('store_id').annotate(count=Count('id'))}
        for s in stores:
            s.visit_count = visit_counts.get(s.id, 0)

        stores = sorted(stores, key=lambda s: (-getattr(s, 'visit_count', 0), s.id))
    elif sort == "distance":
        stores = sorted(stores, key=lambda s: s.distance if s.distance is not None else 999999)
    return render(request, "stores/store-search.html", {
        "stores": stores,
        "categories": categories,
        "selected_gu": selected_gu,
        "query": query or "",
        "selected_category": selected_category,
        "user_lat": user_lat,
        "user_lng": user_lng,
        "sort": sort,
    })


# 가게 상세 페이지
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # 사용자 위치 가져오기
    if request.user.is_authenticated:
        user_lat, user_lng, _ = get_user_location(request.user)
    else:
        # 비로그인 시 기본 위치
        user_lat, user_lng = 37.5665, 126.9780  # 서울시청

    # 거리 계산 (m 단위)
    if store.latitude and store.longitude:
        store.distance = haversine(user_lat, user_lng, store.latitude, store.longitude)
    else:
        store.distance = None

    missions = store.missions.all().order_by('-created_at')  # 모든 미션
    active_missions = [m for m in missions if m.is_active]  # 활성화된 미션

    products = store.products.all()  # 상품 목록

    return render(request, 'stores/store-detail.html', {
        'store': store,
        'missions': active_missions,
        'products': products,
    })

