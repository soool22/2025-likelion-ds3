from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import *
from .forms import MissionForm, AmountInputForm
from django.db.models import Q
from stores.utils import haversine, get_user_location, annotate_distance


################ 점주용 ################

# 챌린지 목록
@login_required
def mission_list(request, store_id):
    store = get_object_or_404(request.user.store_set, id=store_id)
    now = timezone.now()
    status = request.GET.get('status', 'active')  # 버튼 클릭으로 active/past 선택

    # 지난 챌린지 (기간이 지난 챌린지)
    if status == 'past':
        missions = store.missions.filter(end_date__lt=now).order_by('-created_at')
    # 진행 중 챌린지
    else:  
        missions = store.missions.filter(start_date__lte=now, end_date__gte=now).order_by('-created_at')

    return render(request, 'missions/mission-list.html', {
        'store': store,
        'missions': missions,
        'status': status
    })

# 챌린지 생성
@login_required
def mission_create(request, store_id):
    store = get_object_or_404(request.user.store_set, id=store_id)

    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.store = store
            mission.save()
            return redirect('missions:mission-list', store_id=store.id)
    else:
        form = MissionForm()

    return render(request, 'missions/mission-create.html', {
        'form': form,
        'store': store
    })

# 챌린지 수정
@login_required
def mission_update(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, store__owner=request.user)

    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            return redirect('missions:mission-list', store_id=mission.store.id)
    else:
        form = MissionForm(instance=mission)

    return render(request, 'missions/mission-update.html', {'form': form, 'store': mission.store})

# 챌린지 삭제
@login_required
def mission_delete(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, store__owner=request.user)
    if request.method == 'POST':
        store_id = mission.store.id
        mission.delete()
        return redirect('missions:mission-list', store_id=store_id)

    return render(request, 'missions/mission-delete.html', {'mission': mission})

################ 소비자용 ################

# 참여 중인 챌린지 조회
@login_required
def my_mission(request):
    now = timezone.now()
    status = request.GET.get('status', 'active')  # 기본값 active
    
    # 지난 챌린지 (완료 or 기간 지난 챌린지)
    if status == 'past':
        progresses = MissionProgress.objects.filter(
            user=request.user
        ).filter(
            models.Q(is_completed=True) | models.Q(mission__end_date__lt=now)
        ).select_related('mission', 'mission__mission_type', 'mission__store') \
        .order_by('-mission__created_at')
    
    # 진행 중 챌린지
    else:  # active
        progresses = MissionProgress.objects.filter(
            user=request.user,
            is_completed=False,
            mission__start_date__lte=now,
            mission__end_date__gte=now
        ).select_related('mission', 'mission__mission_type', 'mission__store') \
        .order_by('mission__created_at')

    # 추천 챌린지 계산
    user_lat, user_lon, _ = get_user_location(request.user)

    # 이미 진행 중이거나 완료한 챌린지 ID
    excluded_ids = MissionProgress.objects.filter(
        user=request.user
    ).values_list('mission_id', flat=True)

    # 추천 후보
    candidate_missions = Mission.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).exclude(id__in=excluded_ids).select_related('store')

    # 거리 계산
    stores = [m.store for m in candidate_missions]
    stores_with_distance = annotate_distance(stores, user_lat, user_lon)

    # Mission 객체에 distance 속성 연결
    store_distance_map = {store.id: store.distance for store in stores_with_distance}
    for mission in candidate_missions:
        mission.distance = store_distance_map.get(mission.store.id, None)

    # 가까운 순으로 정렬 후 최대 3개
    recommended = sorted(candidate_missions, key=lambda m: m.distance or float('inf'))[:3]
    
    return render(request, "missions/my-mission.html", {
        "progresses": progresses,
        "recommended": recommended,
        "status": status,
    })

# 진행도 업데이트 (누적 방문/기간 내 방문)
@login_required
def update_progress(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    progress, _ = MissionProgress.objects.get_or_create(mission=mission, user=request.user)

    if mission.mission_type.key == 'visit_count':
        # 단순 누적 방문
        progress.current_value += 1

    elif mission.mission_type.key == 'visit_period':
        # 기간 내 방문 횟수 계산
        from visit_rewards.models import Visit
        visit_count = Visit.objects.filter(
            store=mission.store,
            user=request.user,
            visit_time__gte=mission.start_date,
            visit_time__lte=mission.end_date
        ).count()
        progress.current_value = visit_count

    progress.check_completion()
    progress.save()

    return redirect('missions:my-mission')

# 진행도 업데이트 (누적 금액)
@login_required
def update_amount(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, mission_type__key='amount')
    store = mission.store
    
    # 최근 24시간 방문 기록 가져오기
    time_threshold = timezone.now() - timedelta(hours=24)
    recent_visit = Visit.objects.filter(
        user=request.user,
        store=store,
        visit_time__gte=time_threshold
    ).order_by('-visit_time').first()

    if not recent_visit:
        messages.error(request, "최근 24시간 내 방문 인증이 필요합니다.")
        return redirect('stores:store-detail', store.id)

    # 금액 입력 중복 방지
    access_record, _ = VisitAmountAccess.objects.get_or_create(
        user=request.user,
        store=store,
        visit=recent_visit
    )

    if access_record.used:
        messages.error(request, "이미 누적 금액을 입력했습니다.")
        return redirect('stores:store-detail', store.id)
    
    if request.method == 'POST':
        form = AmountInputForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['secret_code']
            if code != store.secret_code:
                messages.error(request, "점주 코드가 일치하지 않습니다.")
            else:
                amount = form.cleaned_data['amount']
                progress, _ = MissionProgress.objects.get_or_create(mission=mission, user=request.user)
                progress.current_value += amount
                progress.check_completion()
                progress.save()

                # 입력 완료 표시
                access_record.used = True
                access_record.save()   # <--- 반드시 저장해야 함

                messages.success(request, f"{amount}원 누적 완료! 남은 금액: {progress.remaining}원")
                return redirect('stores:store-detail', store.id)
    else:
        form = AmountInputForm()

    return render(request, 'missions/update-amount.html', {'form': form, 'mission': mission})

# 챌린지 완료
@login_required
def mission_complete(request, mission_id):
    now = timezone.now()
    mission = get_object_or_404(Mission, id=mission_id, start_date__lte=now, end_date__gte=now)

    completion, created = MissionComplete.objects.get_or_create(mission=mission, user=request.user)

    if created:
        mission.store.visit_count += 1
        mission.store.save()

    return render(request, 'missions/mission-complete.html', {
        'mission': mission,
        'completion': completion,
    })



