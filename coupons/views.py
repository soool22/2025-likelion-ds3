from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserCoupon
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Coupon
from stores.models import Store
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count,Q
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json

# -----------------------------
# 쿠폰 목록
# -----------------------------


@login_required
def coupon_list(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    now = timezone.localtime(timezone.now())
    status = request.GET.get('status', 'active')  # active / past 버튼

    if status == 'past':
        # 만료된 쿠폰: expire_at이 있고 현재보다 이전
        coupons = store.coupons.filter(expire_at__lt=now).order_by('-created_at')
    else:
        # 사용 가능한 쿠폰: expire_at 없거나 현재 이후
        coupons = store.coupons.filter(
            Q(expire_at__gte=now) | Q(expire_at__isnull=True)
        ).order_by('-created_at')

    # 발급 사용자 수
    coupons = coupons.annotate(user_count=Count('usercoupon'))

    return render(request, 'coupons/store_coupon_list.html', {
        'store': store,
        'coupons': coupons,
        'status': status
    })



# -----------------------------
# 쿠폰 생성
# -----------------------------
@login_required
def create_coupon(request, store_id=None):
    user = request.user
    stores = Store.objects.filter(owner=user)

    selected_store = None
    if store_id:
        try:
            selected_store = stores.get(id=store_id)
        except Store.DoesNotExist:
            selected_store = None

    if request.method == 'POST':
        store_id_post = request.POST.get('store')
        name = request.POST.get('name')
        coupon_type = request.POST.get('type')
        expire_at_str = request.POST.get('expire_at')

        store = get_object_or_404(stores, id=store_id_post)

        discount_amount = request.POST.get('discount_amount') if coupon_type == 'amount' else None
        discount_percent = request.POST.get('discount_percent') if coupon_type == 'percent' else None
        gift_item = request.POST.get('gift_item') if coupon_type == 'gift' else None
        custom_text = request.POST.get('custom_text') if coupon_type == 'custom' else None

        # expire_at 문자열 -> timezone-aware datetime
        expire_at = None
        if expire_at_str:
            try:
                expire_at = datetime.fromisoformat(expire_at_str)
                expire_at = timezone.make_aware(expire_at)
            except ValueError:
                messages.error(request, "유효하지 않은 만료일입니다.")
                return redirect(request.path_info)

        Coupon.objects.create(
            store=store,
            name=name,
            coupon_type=coupon_type,
            discount_amount=discount_amount,
            discount_percent=discount_percent,
            gift_item=gift_item,
            custom_text=custom_text,
            expire_at=expire_at
        )
        messages.success(request, f"{name} 쿠폰 발급 완료")
        return redirect('coupons:coupon_list', store_id=store.id)

    context = {
        'stores': stores,
        'selected_store': selected_store
    }
    return render(request, 'coupons/create_coupon.html', context)


# -----------------------------
# 쿠폰 수정
# -----------------------------
@login_required
def update_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id, store__owner=request.user)
    stores = Store.objects.filter(owner=request.user)

    if request.method == 'POST':
        coupon.name = request.POST.get('name')
        coupon_type = request.POST.get('type')
        coupon.coupon_type = coupon_type
        coupon.expire_at = request.POST.get('expire_at') or None

        coupon.discount_amount = request.POST.get('discount_amount') if coupon_type == 'amount' else None
        coupon.discount_percent = request.POST.get('discount_percent') if coupon_type == 'percent' else None
        coupon.gift_item = request.POST.get('gift_item') if coupon_type == 'gift' else None
        coupon.custom_text = request.POST.get('custom_text') if coupon_type == 'custom' else None

        store_id_post = request.POST.get('store')
        coupon.store = stores.get(id=store_id_post)

        coupon.save()
        messages.success(request, f"{coupon.name} 쿠폰 수정 완료")
        return redirect('coupons:coupon_list', store_id=coupon.store.id)

    context = {
        'coupon': coupon,
        'stores': stores,
    }
    return render(request, 'coupons/update_coupon.html', context)


# -----------------------------
# 쿠폰 삭제
# -----------------------------
@login_required
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id, store__owner=request.user)
    store_id = coupon.store.id
    coupon.delete()
    messages.success(request, "쿠폰이 삭제되었습니다.")
    return redirect('coupons:coupon_list', store_id=store_id)


@login_required
@csrf_exempt  # JS fetch로 호출할 때 CSRF token 헤더를 넣었다면 제거 가능
def use_coupon(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST 요청만 허용됩니다."})

    try:
        data = json.loads(request.body)
        coupon_id = data.get("coupon_id")
        secret_code = data.get("secret_code")
        user = request.user

        # 1) 쿠폰 존재 확인
        coupon = Coupon.objects.get(id=coupon_id)

        # 2) 시크릿 코드 검증 (store owner와 비교)
        if secret_code != coupon.store.secret_code:
            return JsonResponse({"success": False, "error": "잘못된 시크릿 코드입니다."})

        # 3) 쿠폰 발급 여부 확인
        user_coupon, created = UserCoupon.objects.get_or_create(user=user, coupon=coupon)

        # 4) 사용 처리
        if not user_coupon.used:
            user_coupon.used = True
            user_coupon.save()
        else:
            return JsonResponse({"success": False, "error": "이미 사용한 쿠폰입니다."})

        return JsonResponse({"success": True})

    except Coupon.DoesNotExist:
        return JsonResponse({"success": False, "error": "쿠폰이 존재하지 않습니다."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})