from background_task import background
from missions.management.commands.update_weekly_ranking import Command

@background(schedule=0)
def update_weekly_ranking_task():
    """
    WeeklyMissionRanking 업데이트 작업
    """
    cmd = Command()
    cmd.handle()
