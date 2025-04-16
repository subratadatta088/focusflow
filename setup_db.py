from models.app_usage import AppUsage
from db.database import db

db.connect()

#drop_tables
db.drop_tables([AppUsage])


#cerate_tables
db.create_tables([AppUsage])
