import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Load biến môi trường từ file .env

class Database:
    def __init__(self):
        try:
            self.con = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASS", ""),
                database=os.getenv("DB_NAME", "quanlydangvien"),
                autocommit=True
            )
            self.cur = self.con.cursor(dictionary=True)
            print("✅ Kết nối cơ sở dữ liệu thành công!")
        except mysql.connector.Error as err:
            print(f"❌ Lỗi kết nối cơ sở dữ liệu: {err}")

    def get_connection(self):
        return self.con, self.cur
