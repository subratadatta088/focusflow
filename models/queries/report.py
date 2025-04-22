from peewee import fn, JOIN
from ..app_activity import AppActivity
from ..app_usage import AppUsage
from ..timer_session import TimerSession
# Assuming `AppUsage` and `AppActivity` are already defined as in your example

def fetch_app_usage_and_activity(date):
    query = (
        AppUsage
        .select(AppUsage, AppActivity)
        .join(AppActivity, 
              on=((AppUsage.app_name == AppActivity.app_name) & 
                  (AppUsage.date == AppActivity.date)), 
              join_type=JOIN.LEFT_OUTER)
        .where(AppUsage.date == date)
    )

    results = []

    for record in query:
        activity = record.appactivity if hasattr(record, 'appactivity') else None

        results.append({
            "app_name": record.app_name,
            "usage_focused_time": record.focused_time,
            "background_time": record.background_time,
            "activity_focused_time": activity.focused_time if activity else 0
        })

    return results


def fetch_timer_sessions(date):
    query = (
        TimerSession
        .select()
        .where(date == date)
    )
    
    results = []
    
    for record in query:
        results.append({
            "start_time": record.start_time,
            "end_time": record.end_time,
            "active_duration":record.active_duration
        })

    return results

def get_total_active_duration(target_date):
    total = (TimerSession
             .select(fn.SUM(TimerSession.active_duration).alias('total'))
             .where(TimerSession.date == target_date)
             .scalar())
    
    return total or 0  # If no sessions, return 0