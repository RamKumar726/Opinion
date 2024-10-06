from ..repositories.user_repository import fetch_user
from ..repositories.otp_repository import generate_new_otp

from utils import check_token, format_success_response, validate_phone_number
from config import Config
import requests
import logging
from datetime import datetime

def handle_auth(data):
    phone_number = data.get('phone_number')
    # if not validate_phone_number(phone_number):
    #     return format_success_response("error", {"message": "Invalid Phone Number"}), 400 
        
    user  = fetch_user(phone_number)
    if user:
        response, status_code = check_token()
        if status_code == 401:
            return format_success_response("error", {"message": "Token is missing or malformed"}), status_code
        elif status_code == 403:
            return format_success_response("error", {"message": "Token expired, please log in again"}), status_code
        
        token_payload = response.get("payload")

        if token_payload['user_id'] == user.id:
            return format_success_response("success", {"message": "Token is valid, login successful"}), 200
        
    otp_send_url = f"https://2factor.in/API/V1/{Config.API_2FA}/SMS/{phone_number}/AUTOGEN"

    try:
        otp_response = requests.get(otp_send_url)
        otp_data = otp_response.json()

        if otp_data['Status'] == 'Success':
            session_id = otp_data['Details']
            expiration_time = datetime.utcnow() + Config.OTP_EXPIRY_TIME
            generate_new_otp(phone_number,session_id,expiration_time)
            
            if user:
                return format_success_response("success", {"message": "OTP sent for login"}), 200
            else:
                return format_success_response("success", {"message": "OTP sent for signup"}), 200

        return format_success_response("error", {"message": "Failed to send OTP"}), 500

    except requests.exceptions.RequestException as e:
        logging.error(f"OTP service request failed: {e}")
        return format_success_response("error", {"message": "OTP service unavailable"}), 500

