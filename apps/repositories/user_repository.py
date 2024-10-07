from ..models.user import User
from apps import db
def fetch_user(mobile_number):
    return User.query.filter_by(mobile_number=mobile_number).first()

def create_user(username,mobile_number):
    new_user =  User(username=username, mobile_number=mobile_number)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def verify_user(mobile_number):
    user =  User.query.filter_by(mobile_number=mobile_number).first()
    if not user.is_mobile_verified:
        user.is_mobile_verified = True
        db.session.commit()
