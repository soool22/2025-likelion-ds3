from django.shortcuts import render, redirect
from .models import Store
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import *
from django.utils import timezone
from .forms import StoreForm
from visit_rewards.models import Visit
from collections import defaultdict
from django.db.models import Count, Avg, F, FloatField, ExpressionWrapper
from ai_services.services import summarize_reviews  # ai_services에서 요약 함수
from datetime import timedelta

################ 점주 ################

# 가게 등록
@login_required
def store_create(request):
    """ # 점주 계정 아닌 경우
    if not request.user.is_owner():
        messages.error(request, '점주 계정만 가게를 등록할 수 있습니다.')
        return redirect('accounts:owner_login')
    """
    # 점주 계정인 경우
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
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

# 모든 가게 목록 (가게 등록 최신 순으로)
def public_store_list(request):
    category_slug = request.GET.get('category')  
    stores = Store.objects.all().order_by('-id')
    
    if category_slug:
        stores = stores.filter(category__slug=category_slug)

    categories = Category.objects.all()  # 상단 필터용 목록
    return render(request, 'stores/public-store-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': category_slug
    })

# 인기 가게 (방문자 높은 순으로)
def popular_store_list(request):
    category_slug = request.GET.get('category')
    today = timezone.localdate()

    # 카테고리 필터링
    stores = Store.objects.all()
    if category_slug:
        stores = stores.filter(category__slug=category_slug)

    # 방문자 수 계산: 하루 최대 2회
    # key = (store_id, user_id), value = 방문 횟수(최대 2)
    visit_counts = defaultdict(int)
    visits_today = Visit.objects.filter(visit_time__date=today)
    for v in visits_today:
        if category_slug and not v.store.category.filter(slug=category_slug).exists():
            continue
        key = (v.store_id, v.user_id)
        visit_counts[key] = min(visit_counts.get(key, 0) + 1, 2)

    # store별 총 방문수 계산
    total_counts = defaultdict(int)
    for (store_id, user_id), count in visit_counts.items():
        total_counts[store_id] += count

    # Store 객체에 visit_count 속성 추가
    for store in stores:
        store.visit_count = total_counts.get(store.id, 0)

    # 방문자 수 높은 순, 같은 방문자 수면 최신 등록 순
    stores = sorted(stores, key=lambda s: (-s.visit_count, -s.id))

    categories = Category.objects.all()
    return render(request, 'stores/popular-store-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': category_slug
    })

# 리뷰 Best (리뷰 평점 높은 순으로)
def review_best_list(request):
    category_slug = request.GET.get('category')
    a, b = 0.7, 0.3

    stores = Store.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).annotate(
        score=ExpressionWrapper(
            (F('avg_rating') * a) + (F('review_count') * b),
            output_field=FloatField()
        )
    ).order_by('-score', '-id')

    if category_slug:
        stores = stores.filter(category__slug=category_slug)

    categories = Category.objects.all()
    return render(request, 'stores/review-best-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': category_slug
    })

# 가게 정보
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = store.products.all()
    missions = store.missions.filter(end_date__gte=timezone.now())

    # 마지막 요약 갱신 30분 이상 지났으면 새로 호출
    if not store.review_summary_updated or timezone.now() - store.review_summary_updated > timedelta(minutes=30):
        store = summarize_reviews(store)

    # 즐겨찾기 여부
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user.favorites.filter(id=store.id).exists()

    # DB에서 가져온 값
    context = {
        'store': store,
        'products': products,
        'missions': missions,
        'ai_summary': store.review_summary_text,
        'review_keywords': store.review_keywords.split(",") if store.review_keywords else [],
        'snippet': store.review_snippet,
        'is_favorite': is_favorite,
    }

    return render(request, 'stores/store-detail.html', context)