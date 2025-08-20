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
        return redirect('/accounts/login/')  # 회원가입 후 로그인 페이지로 리다이렉트


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
    
            return render(request, 'accounts/mypage.html', {'form': form})

    form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/mypage.html', {'form': form})

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

    context = {
        'nickname': user.nickname,
        'email': user.email,
        'preference': preference,  # 마이페이지에서 관심 설정 표시 가능
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

    if request.method == "POST":
        preference.preferred_food = request.POST.get("preferred_food", "")
        preference.preferred_location = request.POST.get("preferred_location", "")
        preference.save()
        return redirect('accounts:mypage')  # 저장 후 마이페이지 이동

    return render(request, 'accounts/user_preferences.html', {'preference': preference})




# -----------------------------
# 찜한 가게 보기
# -----------------------------
@login_required
def favorite_stores(request):
    favorites = FavoriteStore.objects.filter(user=request.user).select_related('store')
    return render(request, 'accounts/favorite_stores.html', {'favorites': favorites})


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
        messages.success(request, "위치가 저장되었습니다.")
        # 저장 후 홈 페이지로 리다이렉트
        return redirect('home:main')  # home 앱의 main 뷰

    context = {
        'saved_address': loc.address,
        'saved_lat': loc.latitude,
        'saved_lng': loc.longitude,
        'saved_gu': loc.gu_name,
    }
    return render(request, 'accounts/user_location.html', context)

