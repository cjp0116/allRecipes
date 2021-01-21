from app import app
from models import db
db.drop_all()
db.create_all()
User.register("api", "api@api.com", "api")
db.session.commit()