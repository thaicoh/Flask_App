import bcrypt
import json
from database import Database
import mysql
import os 
import datetime
import jwt
import mysql.connector
from flask import jsonify, request
from utils.auth import token_required, generate_token



class user_model():
    
    def __init__(self):
        db = Database()
        self.con, self.cur = db.get_connection() 

    @token_required
    def user_getall_model(self):
        self.cur = self.con.cursor(dictionary=True)  # Tạo cursor mới để tránh cache
        self.cur.execute("SELECT * FROM nguoidung")
        rs = self.cur.fetchall()
        self.cur.close()  # Đóng cursor sau khi truy vấn

        if rs:  # Kiểm tra có dữ liệu không
            response = {
                "status": "success",
                "message": "Lấy danh sách người dùng thành công.",
                "data": rs
            }
            return json.dumps(response, ensure_ascii=False), 200  # Mã HTTP 200 OK
        else:
            response = {
                "status": "error",
                "message": "Không có dữ liệu.",
                "data": []
            }
            return json.dumps(response, ensure_ascii=False), 404  # Mã HTTP 404 Not Found

    def user_getinfo_model(self, user_id):
        self.cur = self.con.cursor(dictionary=True)  # Tạo cursor mới để tránh cache
        self.cur.execute("SELECT * FROM nguoidung WHERE MaNguoiDung = %s", (user_id,))
        rs = self.cur.fetchone()
        self.cur.close()  # Đóng cursor sau khi truy vấn

        if rs:  # Nếu tìm thấy user
            response = {
                "status": "success",
                "message": "Lấy thông tin người dùng thành công.",
                "data": rs
            }
            return json.dumps(response, ensure_ascii=False), 200  # Mã HTTP 200 OK
        else:
            response = {
                "status": "error",
                "message": "Không tìm thấy thông tin người dùng.",
                "data": None
            }
            return json.dumps(response, ensure_ascii=False), 404  # Mã HTTP 404 Not Found

    @token_required
    def user_addone_model(self, data):
        try:
            self.cur = self.con.cursor(dictionary=True)  # Tạo cursor mới

            # Kiểm tra nếu TenDangNhap đã tồn tại
            check_sql = "SELECT COUNT(*) AS count FROM nguoidung WHERE TenDangNhap = %s"
            self.cur.execute(check_sql, (data["TenDangNhap"],))
            result = self.cur.fetchone()
            
            if result["count"] > 0:
                return json.dumps({"status": "error", "message": "Tên đăng nhập đã tồn tại!"}, ensure_ascii=False), 409  # HTTP 409: Conflict

            # Băm mật khẩu với bcrypt
            hashed_password = bcrypt.hashpw(data["MatKhauDung"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Câu lệnh SQL sử dụng parameterized query để tránh SQL Injection
            sql = """
            INSERT INTO nguoidung (TenNguoiDung, MatKhauDung, VaiTro, TrangThai, TenDangNhap, MatKhauGoc) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (data["TenNguoiDung"], hashed_password, data["VaiTro"], data["TrangThai"], data["TenDangNhap"], data["MatKhauDung"])

            self.cur.execute(sql, values)  # Thực thi SQL an toàn
            self.con.commit()  # Xác nhận giao dịch

            # Trả về JSON response
            response = {
                "status": "success",
                "message": "User created successfully",
                "user": {
                    "TenNguoiDung": data["TenNguoiDung"],
                    "VaiTro": data["VaiTro"],
                    "TrangThai": data["TrangThai"],
                    "TenDangNhap": data["TenDangNhap"]
                }
            }
            return json.dumps(response, ensure_ascii=False), 201  # HTTP 201: Created

        except mysql.connector.Error as err:
            self.con.rollback()  # Hoàn tác nếu có lỗi
            response = {"status": "error", "message": f"Database error: {str(err)}"}
            return json.dumps(response, ensure_ascii=False), 500  # HTTP 500: Internal Server Error

        except Exception as e:
            response = {"status": "error", "message": f"Unexpected error: {str(e)}"}
            return json.dumps(response, ensure_ascii=False), 400  # HTTP 400: Bad Request

        finally:
            if hasattr(self, "cur"):  # Kiểm tra nếu cursor đã được tạo trước khi đóng
                self.cur.close()


      # Import middleware kiểm tra token

    @token_required
    def user_update_model(self, data, user_id):
        try:
            db = Database()
            self.con, self.cur = db.get_connection() 

            #self.cur = self.con.cursor(dictionary=True)

            # Kiểm tra người dùng có tồn tại không
            self.cur.execute("SELECT * FROM nguoidung WHERE MaNguoiDung = %s", (user_id,))
            user = self.cur.fetchone()
            if not user:
                return jsonify({"status": "error", "message": "Người dùng không tồn tại!"}), 404

            # Cập nhật thông tin người dùng
            sql = """
            UPDATE nguoidung 
            SET TenNguoiDung = %s, VaiTro = %s, TrangThai = %s, TenDangNhap = %s
            WHERE MaNguoiDung = %s
            """
            values = (data['TenNguoiDung'], data['VaiTro'], data['TrangThai'], data['TenDangNhap'], user_id)

            self.cur.execute(sql, values)

            # Nếu có cập nhật mật khẩu mới
            if 'MatKhauDung' in data and data['MatKhauDung'].strip():
                hashed_password = bcrypt.hashpw(data['MatKhauDung'].encode('utf-8'), bcrypt.gensalt())
                self.cur.execute("UPDATE nguoidung SET MatKhauDung = %s, MatKhauGoc = %s WHERE MaNguoiDung = %s",
                                (hashed_password.decode('utf-8'), data['MatKhauDung'], user_id))

            self.con.commit()

            # Lấy lại thông tin người dùng sau khi cập nhật
            self.cur.execute("SELECT MaNguoiDung, TenNguoiDung, VaiTro, TrangThai, TenDangNhap FROM nguoidung WHERE MaNguoiDung = %s", (user_id,))
            updated_user = self.cur.fetchone()

            return jsonify({
                "status": "success",
                "message": "Cập nhật người dùng thành công!",
                "user": updated_user
            }), 200

        except mysql.connector.Error as err:
            self.con.rollback()
            return jsonify({"status": "error", "message": f"Lỗi database: {str(err)}"}), 500

        except Exception as e:
            return jsonify({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}), 400

        finally:
            self.cur.close()


    @token_required 
    def user_delete_model(self, id):
        try:
            self.cur = self.con.cursor(dictionary=True)  # Tạo cursor mới tránh cache

            # 🔹 **1. Lấy user_id từ request (middleware đã kiểm tra token)**
            # Lấy user_id từ token
            user_id = request.user_id
            print("User ID từ token:", user_id)  # Debug xem user_id có đúng không

            # 🔹 **2. Kiểm tra quyền (chỉ admin - vai trò 1 - mới được cập nhật)**
            self.cur.execute("SELECT VaiTro FROM nguoidung WHERE MaNguoiDung = %s", (user_id,))
            user = self.cur.fetchone()

            if not user or user["VaiTro"] != 1:
                return json.dumps({"status": "error", "message": "Bạn không có quyền cập nhật người dùng!"}, ensure_ascii=False), 403

            # 🔹 **4. Tiến hành xóa user**
            sql = "DELETE FROM quanlydangvien.nguoidung WHERE MaNguoiDung = %s"
            self.cur.execute(sql, (id,))

            # Kiểm tra số dòng bị ảnh hưởng
            if self.cur.rowcount > 0:
                self.con.commit()  # Xác nhận xóa
                return json.dumps({"status": "success", "message": "Xóa thành công!", "deleted_id": id}, ensure_ascii=False), 200
            else:
                return json.dumps({"status": "error", "message": "Không tìm thấy bản ghi để xóa.", "deleted_id": id}, ensure_ascii=False), 404

        except mysql.connector.Error as err:
            self.con.rollback()
            return json.dumps({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}, ensure_ascii=False), 500

        except Exception as e:
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400

        finally:
            self.cur.close()  # Đóng cursor

    def user_login_model(self, data):
        try:
            self.cur = self.con.cursor(dictionary=True)  # Tạo cursor mới tránh cache

            # 🔹 **1. Truy vấn lấy thông tin người dùng theo TenDangNhap**
            sql = "SELECT * FROM nguoidung WHERE TenDangNhap = %s"
            self.cur.execute(sql, (data.get("TenDangNhap",),))
            user = self.cur.fetchone()

            if not user:
                return json.dumps({"status": "error", "message": "Tên đăng nhập không tồn tại"}, ensure_ascii=False), 404

            # 🔹 **2. Kiểm tra mật khẩu với bcrypt**
            if bcrypt.checkpw(data.get("MatKhauDung", "Unknown").encode('utf-8'), user['MatKhauDung'].encode('utf-8')):
                
                # ✅ **Tạo JWT Token bằng hàm `generate_token`**
                token = generate_token(user["MaNguoiDung"], user["TenDangNhap"], user["VaiTro"])

                # ✅ **Trả về Token**
                response = {
                    "status": "success",
                    "message": "Đăng nhập thành công",
                    "user": {
                        "MaNguoiDung": user["MaNguoiDung"],  # Đảm bảo API trả về MaNguoiDung
                        "TenNguoiDung": user["TenNguoiDung"],
                        "VaiTro": user["VaiTro"],
                        "TrangThai": user["TrangThai"],
                        "TenDangNhap": user["TenDangNhap"]
                    },
                    "token": token  # Token JWT trả về client
                }
                return json.dumps(response, ensure_ascii=False), 200
            else:
                return json.dumps({"status": "error", "message": "Mật khẩu không đúng"}, ensure_ascii=False), 401

        except Exception as e:
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400

        finally:
            self.cur.close()  # Đóng cursor

