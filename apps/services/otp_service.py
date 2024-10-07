from utils import validate_otp, format_success_response
from ..repositories.otp_repository import fetch_otp, otp_expired, otp_verified, check_otp_entry_limit, delete_otp
from ..repositories.user_repository import fetch_user, create_user, verify_user
from config import Config
from utils import generate_random_username, generate_jwt
import requests
import logging
from datetime import datetime
from apps import db

def handle_verify_otp(data):
    mobile_number = data.get('mobile_number')
    otp_entered = data.get('otp')
    print(mobile_number)
    print(otp_entered)
    if not validate_otp(otp_entered):
        return format_success_response(400, {"error": "Invalid OTP format"}), 400
    otp_record = fetch_otp(mobile_number)

    if otp_record:
        if otp_expired(otp_record):
            return format_success_response(401, {"error": "OTP expired, request a new one"}), 401
        
        session_id = otp_record.otp
        otp_verify_url = f"https://2factor.in/API/V1/{Config.API_2FA}/SMS/VERIFY/{session_id}/{otp_entered}"

        try:
            otp_verify_response = requests.get(otp_verify_url)
            otp_verify_data = otp_verify_response.json()

            if otp_verify_data['Status'] == 'Success':
                otp_verified(otp_record)

                user = fetch_user(mobile_number)

                if not user:
                    username = generate_random_username()
                    new_user = create_user(username=username, mobile_number=mobile_number)

                    user = new_user


                token = generate_jwt(user.user_id, user.mobile_number)
                verify_user(mobile_number)
                return format_success_response(200, {"success": "OTP verified successfully", "token": token}), 200
            elif check_otp_entry_limit(otp_record):
                # If OTP entry attempts exceed the limit, prompt the user to request a new OTP
                delete_otp(otp_record)
                return format_success_response(429, {"error": "You've entered the wrong OTP 5 times. Please request a new OTP."}), 429 

            else:
                if otp_record.expiration_time < datetime.utcnow():
                    db.session.delete(otp_record)
                    db.session.commit()
                    return format_success_response(401, {"error": "OTP expired, request a new one"}), 401
                
            return format_success_response(400, {"error": "Invalid OTP"}), 400

        except requests.exceptions.RequestException as e:
            logging.error(f"OTP verification request failed: {e}")
            return format_success_response(503, {"error": "OTP verification service unavailable"}), 503

    return format_success_response("error", {"message": "OTP session not found"}), 400


        
    