import jwt
import datetime
import os
from flask import jsonify, request
from functools import wraps

# Lấy SECRET_KEY từ biến môi trường hoặc đặt mặc định
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

def generate_token(user_id, ten_dang_nhap, vai_tro):
    payload = {
        "MaNguoiDung": user_id,  # Thêm MaNguoiDung vào token
        "TenDangNhap": ten_dang_nhap,
        "VaiTro": vai_tro,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token):
    """
    Giải mã JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token đã hết hạn."}
    except jwt.InvalidTokenError:
        return {"error": "Token không hợp lệ."}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Token không hợp lệ!"}), 401
        
        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = decoded_token.get("MaNguoiDung")  # Đảm bảo đúng key trong token
            print("User ID trong middleware:", request.user_id)  # Debug
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "Token đã hết hạn!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token không hợp lệ!"}), 401
        
        return f(*args, **kwargs)

    return decorated

