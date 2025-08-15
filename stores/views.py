from django.shortcuts import render, redirect
from .models import Store
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import *
from django.utils import timezone
from .forms import StoreForm

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

    # 방문 수 많은 순 → 같은 방문 수면 최신 등록 순
    stores = Store.objects.all().order_by('-visit_count', '-id')

    if category_slug:
        stores = stores.filter(category__slug=category_slug)

    categories = Category.objects.all()
    return render(request, 'stores/popular-store-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': category_slug
    })

# 리뷰 Best (리뷰 평점 높은 순으로)
def review_best_list(request):
    category_slug = request.GET.get('category')

    # 평점 높은 순으로 정렬 → 같은 방문 수면 최신 등록 순
    stores = Store.objects.all().order_by('-rating', '-id')

    if category_slug:
        stores = stores.filter(category__slug=category_slug)

    categories = Category.objects.all()
    return render(request, 'stores/review-best-list.html', {
        'stores': stores,
        'categories': categories,
        'selected_category': category_slug
    })

# 가게 정보
def store_detail(request,store_id):
    store = get_object_or_404(Store, id=store_id)

    missions = store.missions.all()  # 모든 미션
    active_missions = [m for m in missions if m.is_active]  # property 기반 필터링 (활성화)

    return render(request, 'stores/store-detail.html', {
        'store': store,
        'missions': active_missions,
    })