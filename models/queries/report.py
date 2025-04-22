from peewee import fn, JOIN
from ..app_activity import AppActivity
from ..app_usage import AppUsage
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
