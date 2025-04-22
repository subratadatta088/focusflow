from peewee import DateTimeField, IntegerField, DateField
from datetime import date
from models import BaseModel
from peewee import fn

class TimerSession(BaseModel):
    start_time = DateTimeField()
    end_time = DateTimeField()
    active_duration = IntegerField()  # in seconds
    date = DateField()
    
    
