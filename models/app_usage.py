from peewee import CharField, IntegerField, DateField
from datetime import date
from models import BaseModel
from peewee import fn

class AppUsage(BaseModel):
    app_name = CharField()
    date = DateField()
    focused_time = IntegerField(default=0)
    background_time = IntegerField(default=0)
    
    def flush_to_db(app_dict):
        today = date.today()
        for app, usage in app_dict.items():
            record, created = AppUsage.get_or_create(app_name=app, date=today)
            record.focused_time = (record.focused_time or 0) + usage["focused"]
            record.background_time += usage["background"]
            record.save()
        print("[✓] Flushed to AppUsage DB successfully.")
    
    def get_today_data(today = None):
        today = date.today() if today is None else today
        query = (AppUsage.select().where(AppUsage.date == today))
        print("App Name", "Focused Time", "Background Time")
        for record in query:
            print(record.app_name, record.focused_time, record.background_time)
   