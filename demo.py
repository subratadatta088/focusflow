from models.queries.report import fetch_app_usage_and_activity
from models.app_activity import AppActivity
import datetime,time

date = str(datetime.date.today())
print("report for date: "+ date)
AppActivity.get_today_data()