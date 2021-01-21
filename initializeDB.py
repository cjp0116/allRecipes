from app import setUp, app
from models import connect_db
connect_db(app)
setUp()
