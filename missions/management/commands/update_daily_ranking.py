from django.core.management.base import BaseCommand
from django.utils import timezone
from missions.models import Mission, MissionProgress, MissionComplete, DailyMissionRanking
import datetime

class Command(BaseCommand):
    help = "Update daily mission ranking"

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        today_start = datetime.datetime.combine(today, datetime.time.min).replace(tzinfo=timezone.get_current_timezone())
        today_end = datetime.datetime.combine(today, datetime.time.max).replace(tzinfo=timezone.get_current_timezone())

        self.stdout.write(f"오늘 범위: {today_start} ~ {today_end}")

        # 활성화된 미션만
        active_missions = Mission.objects.filter(start_date__lte=now, end_date__gte=now)

        # 오늘 랭킹에서 종료된 미션 삭제
        day_rankings = DailyMissionRanking.objects.filter(date=today)
        active_ids = active_missions.values_list("id", flat=True)
        day_rankings.exclude(mission_id__in=active_ids).delete()

        for mission in active_missions:
            progress_users = set(
                MissionProgress.objects.filter(
                    mission=mission,
                    updated_at__range=(today_start, today_end)
                ).values_list("user_id", flat=True)
            )
            complete_users = set(
                MissionComplete.objects.filter(
                    mission=mission,
                    completed_at__range=(today_start, today_end)
                ).values_list("user_id", flat=True)
            )

            participants = progress_users | complete_users
            participant_count = len(participants)

            if participant_count > 0:
                DailyMissionRanking.objects.update_or_create(
                    mission=mission,
                    date=today,
                    defaults={
                        "participant_count": participant_count,
                    }
                )

        # 순위 계산
        rankings = DailyMissionRanking.objects.filter(date=today).order_by(
            "-participant_count", "-mission__created_at"
        )
        for idx, ranking in enumerate(rankings, start=1):
            ranking.rank = idx
            ranking.save()

        self.stdout.write(self.style.SUCCESS("✅ Daily mission ranking updated"))
