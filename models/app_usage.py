from peewee import Model, CharField, IntegerField, DateField
from datetime import datetime,date
from models import BaseModel

class AppUsage(BaseModel):
    app_name = CharField()
    date = DateField()
    focused_time = IntegerField(default=0)
    background_time = IntegerField(default=0)
    
    def flush_to_db(app_dict):
        today = date.today()
        for app, usage in app_dict.items():
            record, created = AppUsage.get_or_create(app_name=app, date=today)
            record.focused_time += usage["focused"]
            record.background_time += usage["background"]
            record.save()
        print("[✓] Flushed to DB successfully.")