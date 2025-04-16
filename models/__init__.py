from peewee import *

db = SqliteDatabase('focusflow.db')

class BaseModel(Model):
    class Meta:
        database = db