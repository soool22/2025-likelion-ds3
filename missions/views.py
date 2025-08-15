# missions/views.py
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import MissionForm
from django.contrib import messages

# 미션 목록 (점주용)
@login_required
def mission_list(request, store_id):
    store = get_object_or_404(request.user.store_set, id=store_id)
    missions = store.missions.all()  # 점주 가게의 모든 미션

    return render(request, 'missions/mission-list.html', {
        'store': store,
        'missions': missions
    })

# 미션 생성 (점주용)
@login_required
def mission_create(request, store_id):
    store = get_object_or_404(request.user.store_set, id=store_id)

    if request.method == 'POST':
        form = MissionForm(request.POST)  
        if form.is_valid():
            mission = form.save(commit=False)
            mission.store = store
            mission.save()
            return redirect('missions:mission-list', store_id=mission.store.id)
    else:
        form = MissionForm() 

    return render(request, 'missions/mission-create.html', {'form': form, 'store': store})

# 미션 수정 (점주용)
@login_required
def mission_update(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, store__owner=request.user)

    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            messages.success(request, "미션이 수정되었습니다.")
            return redirect('missions:mission-list', store_id=mission.store.id)
    else:
        form = MissionForm(instance=mission)

    return render(request, 'missions/mission-update.html', {'form': form, 'store': mission.store})

# 미션 삭제 (점주용)
@login_required
def mission_delete(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, store__owner=request.user)
    
    if request.method == 'POST':
        store_id = mission.store.id
        mission.delete()
        messages.success(request, "미션이 삭제되었습니다.")
        return redirect('missions:mission-list', store_id=store_id)

    return render(request, 'missions/mission-delete.html', {'mission': mission})

# 미션 완료 
@login_required
def mission_complete(request, mission_id):
    now = timezone.now()
    mission = get_object_or_404(
        Mission,
        id=mission_id,
        start_date__lte=now,
        end_date__gte=now
    )

    # 이미 완료했는지 확인
    completion, created = MissionComplete.objects.get_or_create(
        mission=mission,
        user=request.user
    )

    if created:
        # 가게 방문 수 +1
        mission.store.visit_count += 1
        mission.store.save()
        message = "미션 완료!"
    else:
        message = "이미 완료한 미션입니다."

    return render(request, 'missions/mission-complete.html', {
        'mission': mission,
        'completion': completion,
        'message': message
    })