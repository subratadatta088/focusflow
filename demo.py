from models.queries.report import fetch_app_usage_and_activity
from models.app_activity import AppActivity
from models.app_usage import AppUsage
import datetime,time

date = str(datetime.date.today())
print("report for date: "+ date)
AppActivity.get_today_data()
AppUsage.get_today_data()
print(fetch_app_usage_and_activity(date))