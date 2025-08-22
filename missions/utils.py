from collections import Counter
from django.utils import timezone
from .models import MissionProgress

def challenge_summary(store):
    today = timezone.localdate()
    
    # 오늘/누적 챌린지 참여
    today_challenges = MissionProgress.objects.filter(
        mission__store=store,
        updated_at__date=today
    ).count()
    total_challenges = MissionProgress.objects.filter(mission__store=store).count()

    # 챌린지 종류별 누적 참여 수
    progresses = MissionProgress.objects.filter(mission__store=store)
    type_counter = Counter(progress.mission.mission_type.key for progress in progresses)

    if type_counter:
        most_participated_type = max(type_counter, key=type_counter.get)
        most_participated_count = type_counter[most_participated_type]
    else:
        most_participated_type = None
        most_participated_count = 0

    challenge_participation = {
        'amount': type_counter.get('amount', 0),
        'visit_count': type_counter.get('visit_count', 0),
        'visit_period': type_counter.get('visit_period', 0),
    }

    return {
        'today_challenges': today_challenges,
        'total_challenges': total_challenges,
        'most_participated_type': most_participated_type,
        'most_participated_count': most_participated_count,
        'challenge_participation': challenge_participation,
    }