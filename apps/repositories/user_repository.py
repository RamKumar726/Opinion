from ..models.user import User
from apps import db
def fetch_user(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()

def create_user(username,phone_number):
    new_user =  User(username=username, phone_number=phone_number)
    db.session.add(new_user)
    db.session.commit()
    return new_user