from peewee import Model, CharField, IntegerField, DateField
from datetime import datetime,date
from models import BaseModel

class AppActivity(BaseModel):
    app_name = CharField()
    date = DateField()
    focused_time = IntegerField(default=0)
    
    def flush_to_db(app_dict):
        today = date.today()
        for app, usage in app_dict.items():
            record, created = AppActivity.get_or_create(app_name=app, date=today)
            record.focused_time += usage["focused"]
            record.save()
        print("[✓] Flushed to DB successfully.")