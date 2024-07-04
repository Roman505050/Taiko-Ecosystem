import jwt
from datetime import datetime, timezone, timedelta


def check_jwt_expiry(token):
    """
    Check JWT token expiration against GMT+3 timezone and whether less than 16 hours left.

    :param token: JWT token to check
    :return: True if token is valid (not expired or less than 16 hours left), False otherwise
    """
    try:
        decoded_payload = jwt.decode(token, options={"verify_signature": False})
        
        current_time = datetime.now(timezone.utc)
        gmt_plus_3 = timedelta(hours=3)
        current_time_gmt_plus_3 = current_time + gmt_plus_3
        
        if 'exp' in decoded_payload:
            expiration_time = datetime.fromtimestamp(decoded_payload['exp'], timezone.utc)
            time_left = expiration_time - current_time_gmt_plus_3
            is_valid = time_left.total_seconds() > 16 * 3600  # 16 hours in seconds
        else:
            # If 'exp' claim is missing, assume token is invalid
            is_valid = False
        
        return is_valid
    
    except jwt.ExpiredSignatureError:
        # JWT has expired
        return False
    except jwt.InvalidTokenError:
        # Invalid token
        return False
    except Exception as e:
        # Other exceptions
        print(f"Error checking JWT expiry: {e}")
        return False
