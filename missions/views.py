# missions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import MissionForm, AmountInputForm

################ 점주용 ################

# 챌린지 목록
@login_required
def mission_list(request, store_id):
    store = get_object_or_404(request.user.store_set, id=store_id)
    missions = store.missions.all()  # 점주 가게의 모든 챌린지
    return render(request, 'missions/mission-list.html', {
        'store': store,
        'missions': missions
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
            # 참여자 수 갱신 (처음 생성 시 0으로 초기화)
            mission.update_participants_count()
            return redirect('missions:mission-list', store_id=mission.store.id)
    else:
        form = MissionForm()

    return render(request, 'missions/mission-create.html', {'form': form, 'store': store})

# 챌린지 수정
@login_required
def mission_update(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, store__owner=request.user)

    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            # 수정 후 참여자 수 갱신
            mission.update_participants_count()
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
    progresses = MissionProgress.objects.filter(user=request.user).select_related('mission', 'mission__mission_type', 'mission__store')
    return render(request, "missions/my-mission.html", {"progresses": progresses})

# 진행도 업데이트 (누적 방문/기간 내 방문)
@login_required
def update_progress(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    progress, _ = MissionProgress.objects.get_or_create(mission=mission, user=request.user)

    if mission.mission_type.key in ['visit_count', 'period_visit']:
        progress.current_value += 1
        progress.check_completion()
        progress.save()

        # 참여자 수 갱신
        mission.update_participants_count()

    return redirect('missions:my-missions')

# 진행도 업데이트 (누적 금액)
@login_required
def update_amount(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, mission_type__key='amount')
    store = mission.store

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

                # 참여자 수 갱신
                mission.update_participants_count()

                messages.success(request, f"{amount}원 누적 완료! 남은 금액: {progress.remaining}원")
                return redirect('stores:store-detail', store.id)
    else:
        form = AmountInputForm()

    return render(request, 'missions/update-amount.html', {'form': form, 'mission': mission})

# 미션 완료
@login_required
def mission_complete(request, mission_id):
    now = timezone.now()
    mission = get_object_or_404(Mission, id=mission_id, start_date__lte=now, end_date__gte=now)

    completion, created = MissionComplete.objects.get_or_create(mission=mission, user=request.user)

    if created:
        mission.store.visit_count += 1
        mission.store.save()
        message = "챌린지 완료!"
    else:
        message = "이미 완료한 챌린지입니다."

    # 참여자 수 갱신
    mission.update_participants_count()

    return render(request, 'missions/mission-complete.html', {
        'mission': mission,
        'completion': completion,
        'message': message
    })



