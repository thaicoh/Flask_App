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
                autocommit=True,
                connect_timeout=28800  # Thời gian chờ kết nối (giây)
            )
            self.cur = self.con.cursor(dictionary=True)
            print("✅ Kết nối cơ sở dữ liệu thành công!")

            # Lấy danh sách các bảng trong cơ sở dữ liệu
            self.show_tables()

        except mysql.connector.Error as err:
            print(f"❌ Lỗi kết nối cơ sở dữ liệu: {err}")

    def get_connection(self):
        return self.con, self.cur

    def show_tables(self):
        try:
            # Thực hiện câu lệnh SQL để lấy danh sách các bảng
            self.cur.execute("SHOW TABLES")
            tables = self.cur.fetchall()
            
            print("Danh sách các bảng trong cơ sở dữ liệu:")
            for table in tables:
                print(table['Tables_in_' + os.getenv("DB_NAME", "quanlydangvien")])
        except mysql.connector.Error as err:
            print(f"❌ Lỗi khi lấy danh sách bảng: {err}")


    def close(self):
        """Đóng kết nối và cursor khi không còn sử dụng."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()
        print("✅ Đóng kết nối cơ sở dữ liệu thành công!")

# Tạo đối tượng Database và kết nối
db = Database()

