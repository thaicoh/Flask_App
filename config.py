import os
from dotenv import load_dotenv

load_dotenv()  # Load biến môi trường từ .env

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "2b34ece4d60b3664f3fa886c7afea56608541b1df1e50aeebee129a1ec4f4eb5")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "quanlydangvien")
