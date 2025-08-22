from django.shortcuts import get_object_or_404, render,redirect
from django.http import JsonResponse, HttpResponse
from .models import Store, Visit
import uuid, base64, qrcode
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.db.models import Sum
from django.views.decorators.http import require_POST
import json
from django.db.models import Count,Q
from django.utils import timezone
from missions.models import Mission, MissionProgress
from coupons.models import UserCoupon

# 방문 인증 페이지 + QR 생성
def visit_check(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # QR 토큰 생성
    if not store.qr_token:
        store.qr_token = uuid.uuid4().hex
        store.save()

    # 방문 인증 API URL 생성
    qr_url = f"{request.scheme}://{request.get_host()}/visit_rewards/visit/?token={store.qr_token}&test=1"

    # QR 코드 생성
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_base64 = base64.b64encode(buf.read()).decode('utf-8')
    store_qr_url = f"data:image/png;base64,{qr_base64}"
    
    # 누적 금액 챌린지
    now = timezone.now()
    has_amount_mission = Mission.objects.filter(
        store=store,
        mission_type__key='amount',  # 누적 금액 챌린지
        start_date__lte=now,
        end_date__gte=now,
    ).exists()

    return render(request, 'visit_rewards/visit_checking.html', {
        'store': store,
        'store_qr_url': store_qr_url,
        'qr_url': qr_url,  # JS fetch용
        'has_amount_mission': has_amount_mission,
    })

@login_required
def visit_store(request):
    token = request.GET.get("token")
    if not token:
        return JsonResponse({"status": "error", "message": "token이 없습니다."}, status=400)

    try:
        is_test = bool(int(request.GET.get("test", 0)))
    except ValueError:
        is_test = False

    store = get_object_or_404(Store, qr_token=token)

    # 방문 인증 생성
    visit = Visit.objects.create(store=store, test=is_test, user=request.user)
    
    # ##### 챌린지 인증 추가(누적 방문, 기간 내 방문) #####
    now = timezone.now()
    missions = Mission.objects.filter(
        store=store,
        start_date__lte=now,
        end_date__gte=now,
        mission_type__key__in=['visit_count', 'visit_period']
    )

    for mission in missions:
        progress, _ = MissionProgress.objects.get_or_create(mission=mission, user=request.user)
        if mission.mission_type.key == 'visit_count':
            progress.current_value += 1
        elif mission.mission_type.key == 'visit_period':
            # Visit 테이블에서 DB 반영 후 카운트
            visit_count = Visit.objects.filter(
                store=store,
                user=request.user,
                visit_time__gte=mission.start_date,
                visit_time__lte=mission.end_date
            ).count()
            progress.current_value = visit_count
        progress.check_completion()
        progress.save()
    # ###############################

    # 포인트 적립 (예: 방문 인증 1000포인트)
    points_earned = 1000
    Reward.objects.create(
        user=request.user,
        reward_type='visit',
        amount=points_earned,
        related_visit=visit
    )

    request.user.points += points_earned
    request.user.save()

    # 로그인 사용자 기준 누적 방문 횟수
    total_visits = Visit.objects.filter(store=store, user=request.user).count()

    # 누적 금액 챌린지 존재 여부
    now = timezone.now()
    amount_mission = Mission.objects.filter(
        store=store,
        mission_type__key='amount',
        start_date__lte=now,
        end_date__gte=now,
    ).first()

    # 이미 완료했는지 확인
    if amount_mission:
        has_amount_mission = True
        completed_amount_mission = MissionProgress.objects.filter(
            mission=amount_mission,
            user=request.user,
            is_completed=True
        ).exists()
    else:
        has_amount_mission = False
        completed_amount_mission = False

    return JsonResponse({
        "status": "ok",
        "store_name": store.name,
        "total_visits": total_visits,
        "points_earned": points_earned,
        "store_id": store.id,
        "has_amount_mission": has_amount_mission,
        "completed_amount_mission": completed_amount_mission,
    })
    
@login_required
def visit_history(request):
    # 로그인 사용자의 방문 내역 (최근 순)
    visits = Visit.objects.filter(user=request.user).select_related('store').order_by('-visit_time')

    # 가장 많이 방문한 가게 (중복 방문 카운트)
    most_visited = (
        visits
        .values('store', 'store__name', 'store__id')
        .annotate(visits_count=Count('id'))
        .order_by('-visits_count')
    ).first()

    # 가장 최근에 방문한 가게
    latest_visit = visits.first()

    return render(request, 'visit_rewards/visit_history.html', {
        'visits': visits,
        'most_visited': most_visited,
        'latest_visit': latest_visit,
    })


#이 위로 방문인증 관련
#-----------------------------------------------------------------------
#이 밑으로 리워드 관련

@login_required
def my_rewards(request):
    """유저가 가진 포인트와 아이템 확인"""

    # 방문 인증 포인트
    visit_points = Reward.objects.filter(user=request.user, reward_type='visit', amount__gt=0, used=False).aggregate(total=Sum('amount'))['total'] or 0
    # 챌린지 포인트
    challenge_points = Reward.objects.filter(user=request.user, reward_type='point', amount__gt=0, used=False).aggregate(total=Sum('amount'))['total'] or 0
    
    total_points = visit_points + challenge_points  # 합산해서 계산용

    # 사용되지 않은 꾸미기 아이템
    items_qs = Reward.objects.filter(
        user=request.user,
        item__isnull=False,
        used=False
    ).select_related('item')
    items = list({r.item for r in items_qs})

    # 보유 기프티콘
    gifticons_qs = Reward.objects.filter(
        user=request.user,
        gifticon__isnull=False,
        used=False
    ).select_related('gifticon')
    gifticons = list({r.gifticon for r in gifticons_qs})

    return render(request, 'visit_rewards/my_rewards.html', {
        'visit_points': visit_points,
        'challenge_points': challenge_points,
        'points': total_points,
        'items': items,
        'gifticons': gifticons,
    })


@login_required
def my_character(request):
    """구매 가능한 꾸미기 아이템 목록"""
    items = Item.objects.all()
    user_points = Reward.objects.filter(user=request.user, amount__gt=0, used=False).aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'visit_rewards/my_character.html', {'items': items, 'user_points': user_points})


@login_required
def buy_item(request, item_id):
    """포인트로 꾸미기 아이템 구매"""
    item = get_object_or_404(Item, pk=item_id)
    user_points = Reward.objects.filter(user=request.user, amount__gt=0, used=False).aggregate(total=Sum('amount'))['total'] or 0

    if user_points < item.point_cost:
        messages.error(request, f"포인트가 부족합니다. 현재 {user_points}점, 아이템 비용 {item.point_cost}점")
        return redirect('visit_rewards:my_character')

    # 포인트 차감
    remaining_cost = item.point_cost
    rewards = Reward.objects.filter(user=request.user, amount__gt=0, used=False).order_by('created_at')
    for r in rewards:
        if r.amount >= remaining_cost:
            r.amount -= remaining_cost
            if r.amount == 0:
                r.used = True
            r.save()
            break
        else:
            remaining_cost -= r.amount
            r.amount = 0
            r.used = True
            r.save()

    # 구매 기록 생성
    PurchaseHistory.objects.create(user=request.user, item=item, points_spent=item.point_cost)

    # 아이템 지급
    Reward.objects.create(user=request.user, item=item, amount=0)

    messages.success(request, f"{item.name} 아이템을 구매했습니다!")
    return redirect('visit_rewards:my_rewards')


@login_required
def shop_gifticons(request):
    """구매 가능한 기프티콘 목록"""
    # 모든 기프티콘 가져오기
    gifticons = Gifticon.objects.all()

    # 유저 현재 포인트 계산
    user_points = Reward.objects.filter(
        user=request.user,
        amount__gt=0,
        used=False
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 각 기프티콘별 구매 후 잔여 포인트 계산
    for g in gifticons:
        g.remaining_points = user_points - g.point_cost

    return render(request, 'visit_rewards/gifticon_shop.html', {
        'gifticons': gifticons,
        'user_points': user_points,
    })

@login_required
def buy_gifticon(request, gifticon_id):
    """포인트로 기프티콘 구매"""
    gifticon = get_object_or_404(Gifticon, pk=gifticon_id)
    user_points = Reward.objects.filter(user=request.user, amount__gt=0, used=False).aggregate(total=Sum('amount'))['total'] or 0

    if user_points < gifticon.point_cost:
        messages.error(request, f"포인트가 부족합니다. 현재 {user_points}점, 기프티콘 비용 {gifticon.point_cost}점")
        return redirect('visit_rewards:shop_gifticons')

    # 포인트 차감
    remaining_cost = gifticon.point_cost
    rewards = Reward.objects.filter(user=request.user, amount__gt=0, used=False).order_by('created_at')
    for r in rewards:
        if r.amount >= remaining_cost:
            r.amount -= remaining_cost
            if r.amount == 0:
                r.used = True
            r.save()
            break
        else:
            remaining_cost -= r.amount
            r.amount = 0
            r.used = True
            r.save()

    # 구매 기록 생성
    PurchaseHistory.objects.create(user=request.user, gifticon=gifticon, points_spent=gifticon.point_cost)

    # 기프티콘 지급
    Reward.objects.create(user=request.user, gifticon=gifticon, amount=0)

    messages.success(request, f"{gifticon.name} 기프티콘을 구매했습니다!")
    return redirect('visit_rewards:my_rewards')


from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from coupons.models import UserCoupon
from visit_rewards.models import Reward


@login_required
def my_gifticons(request):
    now = timezone.localtime(timezone.now())

    # 사용하지 않은, 만료되지 않은 쿠폰
    user_coupons_qs = UserCoupon.objects.filter(
        user=request.user,
        used=False
    ).filter(
        Q(coupon__expire_at__gte=now) | Q(coupon__expire_at__isnull=True)
    ).select_related('coupon', 'coupon__store').order_by('-assigned_at')

    coupons = []
    for uc in user_coupons_qs:
        coupon = uc.coupon
        remaining = None
        if coupon.expire_at:
            delta = coupon.expire_at - now
            if delta.total_seconds() > 0:
                days = delta.days
                hours, rem = divmod(delta.seconds, 3600)
                minutes, _ = divmod(rem, 60)
                remaining = f"{days}일 {hours}시간 {minutes}분 남음"
        coupons.append({
            'id': coupon.id,
            'name': coupon.name,
            'type': coupon.get_coupon_type_display(),
            'discount_amount': coupon.discount_amount,
            'discount_percent': coupon.discount_percent,
            'gift_item': coupon.gift_item,
            'custom_text': coupon.custom_text,
            'expire_at': coupon.expire_at,
            'store': coupon.store,
            'user_count': uc.coupon.usercoupon_set.count(),
            'remaining': remaining,
        })

    # 기프티콘
    gifticons = Reward.objects.filter(
        user=request.user,
        gifticon__isnull=False,
        used=False
    ).select_related('gifticon')

    return render(request, 'visit_rewards/my_gifticons.html', {
        'coupons': coupons,
        'gifticons': gifticons,
    })

@login_required
@require_POST
def use_gifticon(request):
    """체크박스로 기프티콘 사용 처리"""
    try:
        data = json.loads(request.body)
        reward_id = data.get("id")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"success": False, "error": "잘못된 요청"}, status=400)

    reward = get_object_or_404(Reward, id=reward_id, user=request.user, gifticon__isnull=False)

    if reward.used:
        return JsonResponse({"success": False, "error": "이미 사용된 기프티콘"}, status=400)

    reward.used = True
    reward.save()

    return JsonResponse({"success": True})

@login_required
def use_coupon(request):
    """사용자가 점주 시크릿 코드 입력 후 쿠폰 사용 처리"""
    if request.method == "POST":
        data = json.loads(request.body)
        coupon_id = data.get("coupon_id")
        secret_code = data.get("secret_code")

        try:
            user_coupon = UserCoupon.objects.get(user=request.user, coupon_id=coupon_id, used=False)
        except UserCoupon.DoesNotExist:
            return JsonResponse({"success": False, "error": "쿠폰이 존재하지 않거나 이미 사용됨."})

        if secret_code != user_coupon.coupon.store.secret_code:
            return JsonResponse({"success": False, "error": "시크릿 코드가 올바르지 않습니다."})

        user_coupon.mark_used()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "POST 요청이 필요합니다."})


@login_required
def purchase_history(request):
    """
    현재 유저의 기프티콘 구매 내역
    """
    history = PurchaseHistory.objects.filter(user=request.user).select_related('gifticon').order_by('-purchased_at')
    
    # 각 구매 내역마다 사용 여부 표시
    for ph in history:
        ph.used = Reward.objects.filter(user=request.user, gifticon=ph.gifticon, used=True).exists()
    
    return render(request, 'visit_rewards/purchase_history.html', {
        'purchase_history': history
    })
