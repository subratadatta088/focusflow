from peewee import fn, JOIN
from ..app_activity import AppActivity
from ..app_usage import AppUsage
# Assuming `AppUsage` and `AppActivity` are already defined as in your example

def fetch_app_usage_and_activity(date):
    query = (
        AppUsage
        .select(AppUsage.app_name,
                AppUsage.focused_time.alias('usage_focused_time'),
                AppUsage.background_time,
                AppActivity.focused_time.alias('activity_focused_time'))
        .join(AppActivity, on=(AppUsage.app_name == AppActivity.app_name) & (AppUsage.date == AppActivity.date), join_type= JOIN.LEFT_OUTER)
        .where(AppUsage.date == date)
    )
    
    results = []

    for record in query:
        results.append({
            "app_name": record.app_name,
            "usage_focused_time": record.usage_focused_time,
            "background_time": record.background_time,
            "activity_focused_time": getattr(record, 'activity_focused_time', 'Field not available')
        })
    
    return results
