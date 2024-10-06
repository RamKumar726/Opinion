# apps/repositories/otp_repository.py
from apps import db
from utils import format_success_response  
from ..models.otp import Otp
from datetime import datetime, timedelta

def generate_new_otp(phone_number, session_id, expiration_time):
    new_otp_session = Otp(phone_number=phone_number, otp=session_id, expiration_time=expiration_time)
    db.session.add(new_otp_session)
    db.session.commit()

def fetch_otp(phone_number):
    otp =  Otp.query.filter_by(phone_number=phone_number, is_verified=0).first()
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
    if otp_record.failed_attempts >= 3:
        return True
    db.session.commit()


