from models.app_usage import AppUsage
from models.app_activity import AppActivity
from db.database import db

db.connect()

#drop_tables
# db.drop_tables([AppUsage])


#cerate_tables
db.create_tables([AppUsage,AppActivity])
