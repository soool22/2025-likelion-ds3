from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from users.models import UserPreference, FavoriteStore
from .forms import SignUpForm, UserUpdateForm
from stores.models import Store
import os

from visit_rewards import *

from .models import UserLocation
# ========== 기능 API 뷰 ==========

def signup(request):
    if request.method == "GET":
        return render(request, "accounts/signup.html", {'form': SignUpForm()})

    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save()
        user.nickname = form.cleaned_data.get("nickname", "")
        user.save()

        # 새 계정이면 UserPreference 생성
        UserPreference.objects.create(user=user)
        return redirect("accounts:login")  # 회원가입 후 로그인 페이지로 리다이렉트


    return render(request, "accounts/signup.html", {'form': form})

def login(request):
    if request.method == "GET":
        return render(request, "accounts/login.html", {"form": AuthenticationForm()})

    form = AuthenticationForm(request, request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        return redirect('accounts:start-page')

    return render(request, "accounts/login.html", {'form': form})

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('accounts:login')  # 로그인으로 이동

@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        auth_logout(request)  
        messages.success(request, "회원 탈퇴가 완료되었습니다.")
        return redirect('accounts:login')  # 메인 페이지로 이동
    # GET 요청 등 예외 처리 (선택)
    return redirect('accounts:mypage')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필이 수정되었습니다.")
            return redirect('accounts:mypage')
        else:
    
            return render(request, 'accounts/profile_edit.html', {'form': form})

    form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def user_info_view(request):
    user = request.user
    
    context = {
        'username': user.username,
        'nickname': getattr(user, 'nickname', ''),
    }
    return render(request, 'accounts/user_info.html', context)

# ========== 페이지 렌더링 뷰 ==========

# 메인 화면 (소비자/점주로 시작)
def start_page(request):
    return render(request, "accounts/start-page.html")


def signup_page_view(request):
    return render(request, 'accounts/signup.html')


def login_page_view(request):
    return render(request, 'accounts/login.html')

def visit_check(request):
    return render(request, 'visit_rewards/visit_checking.html')

@login_required
def my_page_view(request):
    user = request.user
    # UserPreference 가져오기 (없으면 생성)
    preference, _ = UserPreference.objects.get_or_create(user=user)

    # 문자열로 저장된 선호 항목들을 리스트로 변환
    preferred_categories_list = preference.preferred_categories.split(",") if preference.preferred_categories else []
    preferred_tastes_list = preference.preferred_tastes.split(",") if preference.preferred_tastes else []
    preferred_price_ranges_list = preference.preferred_price_ranges.split(",") if preference.preferred_price_ranges else []
    preferred_health_list = preference.preferred_health.split(",") if preference.preferred_health else []

    context = {
        'nickname': user.nickname,
        'email': user.email,
        'preference': preference,
        'preferred_categories_list': preferred_categories_list,
        'preferred_tastes_list': preferred_tastes_list,
        'preferred_price_ranges_list': preferred_price_ranges_list,
        'preferred_health_list': preferred_health_list,
    }
    return render(request, 'accounts/mypage.html', context)





def terms_or_policy_view(request, page_type):
    # page_type에 따라 파일 경로, 제목을 결정
    if page_type == 'terms':
        file_name = 'terms_of_service.txt'
        title = '서비스 이용약관'
    elif page_type == 'privacy':
        file_name = 'privacy_policy.txt'
        title = '개인정보처리방침'
    else:
        # 알 수 없는 page_type이면 404 처리 (선택사항)
        from django.http import Http404
        raise Http404("Page not found")

    file_path = os.path.join(settings.BASE_DIR, 'policies', file_name)
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    context = {
        'title': title,
        'content': content,
    }
    return render(request, 'accounts/terms/terms_page.html', context)



#------------------------------------------------------------------


# -----------------------------
# 관심 설정 (UserPreference)
# -----------------------------
@login_required
def user_preferences(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)

    categories = ["한식","중식","일식","양식","베이커리","카페","주점","편의점"]
    tastes = ["매운맛","단맛","짠맛","고소한맛","새콤한맛","담백한맛"]
    price_ranges = ["저가","중가","고가"]
    health_options = ["저염식","채식","비건","고단백","저탄수"]

    if request.method == "POST":
        preference.preferred_categories = ",".join(request.POST.getlist("preferred_categories"))
        preference.preferred_tastes = ",".join(request.POST.getlist("preferred_tastes"))
        preference.preferred_price_ranges = ",".join(request.POST.getlist("preferred_price_ranges"))
        preference.preferred_health = ",".join(request.POST.getlist("preferred_health"))
        preference.save()
        return redirect("accounts:mypage")

    context = {
        "preference": preference,
        "categories": categories,
        "tastes": tastes,
        "price_ranges": price_ranges,
        "health_options": health_options,
        "selected_categories": preference.preferred_categories.split(",") if preference.preferred_categories else [],
        "selected_tastes": preference.preferred_tastes.split(",") if preference.preferred_tastes else [],
        "selected_price_ranges": preference.preferred_price_ranges.split(",") if preference.preferred_price_ranges else [],
        "selected_health": preference.preferred_health.split(",") if preference.preferred_health else [],
    }
    return render(request, "accounts/user_preferences.html", context)


# -----------------------------
# 찜한 가게 보기
# -----------------------------

from stores.views import filter_stores
@login_required
def favorite_stores(request):
    # 찜한 가게들 가져오기
    favorites = FavoriteStore.objects.filter(user=request.user).select_related('store')

    # 찜한 가게들의 Store만 추출
    stores = Store.objects.filter(id__in=favorites.values_list('store_id', flat=True))

    # public_store_list와 동일하게 필터링 적용
    stores, categories, user_lat, user_lng, selected_gu, selected_category = filter_stores(request, stores)

    return render(request, 'accounts/favorite_stores.html', {
        'favorites': favorites,   # 기존 찜 정보 (찜 ID 등 필요할 수 있어서 유지)
        'stores': stores,         # 필터된 스토어들
        'categories': categories,
        'selected_category': selected_category,
        'selected_gu': selected_gu,
        'user_lat': user_lat,
        'user_lng': user_lng,
    })
# -----------------------------
# 찜/해제 Ajax
# -----------------------------
from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_favorite(request):
    store_id = request.POST.get("store_id")
    store = get_object_or_404(Store, id=store_id)

    favorite, created = FavoriteStore.objects.get_or_create(user=request.user, store=store)
    if not created:
        favorite.delete()
        return JsonResponse({"status": "removed"})
    return JsonResponse({"status": "added"})

# -----------------------------
# 사용자 위치 설정
# -----------------------------
@login_required
def user_location(request):
    """
    사용자 위치 설정 페이지 + 저장 처리
    """
    loc, _ = UserLocation.objects.get_or_create(user=request.user)

    if request.method == "POST":
        loc.gu_name = request.POST.get("gu_name")
        loc.address = request.POST.get("address")
        loc.latitude = request.POST.get("latitude")
        loc.longitude = request.POST.get("longitude")
        loc.save()
        # 저장 후 홈 페이지로 리다이렉트
        return redirect('home:main')  # home 앱의 main 뷰

    context = {
        'saved_address': loc.address,
        'saved_lat': loc.latitude,
        'saved_lng': loc.longitude,
        'saved_gu': loc.gu_name,
    }
    return render(request, 'accounts/user_location.html', context)

