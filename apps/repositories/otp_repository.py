# apps/repositories/otp_repository.py
from apps import db
from utils import format_success_response  
from ..models.otp import Otp
from datetime import datetime, timedelta

def generate_new_otp(mobile_number, session_id, expiration_time):
    new_otp_session = Otp(mobile_number=mobile_number, otp=session_id, expiration_time=expiration_time)
    db.session.add(new_otp_session)
    db.session.commit()

def fetch_otp(mobile_number):
    otp =  Otp.query.filter_by(mobile_number=mobile_number, is_verified=0).first()
    print(otp)
    return otp

def otp_expired(otp_record):
    if otp_record.expiration_time < datetime.utcnow():
        db.session.delete(otp_record)
        db.session.commit()
        return True

def otp_verified(otp_record):
    otp_record.is_verified = True
    otp_record.failed_attempts = 0  # Reset failed attempts
    db.session.commit()


def check_otp_entry_limit(otp_record):
    otp_record.failed_attempts += 1
    db.session.commit()
    if otp_record.failed_attempts >= 5:
        return True
    
def delete_otp(otp_record):
    db.session.delete(otp_record)
    db.session.commit()



