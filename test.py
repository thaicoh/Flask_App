import jwt

SECRET_KEY = "2b34ece4d60b3664f3fa886c7afea56608541b1df1e50aeebee129a1ec4f4eb5"  # Thay bằng SECRET_KEY thật
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJUZW5EYW5nTmhhcCI6IkFkbWluIiwiVmFpVHJvIjoxLCJleHAiOjE3NDA4NTYwNzJ9.Cbppu7jNOY7hxQLXU_xA5Tey3F-OLSoTSgmnIpYO-F0"

try:
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print("Token decoded:", decoded_token)
except jwt.ExpiredSignatureError:
    print("Token đã hết hạn!")
except jwt.InvalidTokenError:
    print("Token không hợp lệ!")
