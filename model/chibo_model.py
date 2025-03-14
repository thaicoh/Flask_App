import bcrypt
import json
from database import Database
import mysql.connector
import os 
import datetime
import jwt
from flask import request
from utils.auth import token_required, generate_token
from flask import jsonify
import datetime

class chibo_model:
    def __init__(self):
        db = Database()
        self.con, self.cur = db.get_connection()

    @token_required
    def chibo_update_model(self, MaChiBo, request):
        print("MaChiBo:", MaChiBo)

        data = request.get_json()
        print("Dữ liệu JSON nhận được:", data)

        user_role = request.vaitro
        if user_role != 1:
            return jsonify({"status": "error", "message": "Bạn không có quyền cập nhật dữ liệu."}), 403
        
        try:
            self.cur = self.con.cursor(dictionary=True)

            # Kiểm tra đảng viên có tồn tại không
            self.cur.execute("SELECT * FROM quanlydangvien.chibo WHERE MaChiBo = %s", (MaChiBo,))
            existing = self.cur.fetchone()
            if not existing:
                return jsonify({"status": "error", "message": "Không tìm thấy đảng viên"}), 404

            
            # Chỉ cập nhật các trường có trong request
            update_fields = []
            values = []
            for field in data:
                if field in existing:  # Chỉ cập nhật nếu trường tồn tại
                    update_fields.append(f"{field} = %s")
                    values.append(data[field])

            if not update_fields:
                return jsonify({"status": "error", "message": "Không có dữ liệu nào để cập nhật"}), 400

            values.append(MaChiBo)
            sql = f"UPDATE quanlydangvien.chibo SET {', '.join(update_fields)} WHERE MaChiBo = %s"
            self.cur.execute(sql, values)

            self.con.commit()
            return jsonify({"status": "success", "message": "Cập nhật thành công"}), 200

        except mysql.connector.Error as err:
            self.con.rollback()
            return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500

        except Exception as e:
            return jsonify({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}), 400

        finally:
            self.cur.close()
        
    @token_required 
    def chibo_delete_model(self, id):
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
                return json.dumps({"status": "error", "message": "Bạn không có quyền xóa chi bộ!"}, ensure_ascii=False), 403

            # 🔹 **4. Tiến hành xóa user**
            sql = "DELETE FROM quanlydangvien.chibo WHERE MaChiBo = %s"
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

    @token_required
    def chibo_add_model(self, request):
        # Lấy vai trò từ request
        user_role = request.vaitro
        print("Vai trò người dùng:", user_role)  # Debug

        # Kiểm tra vai trò trước khi thực hiện cập nhật
        if user_role != 1:  # Nếu VaiTro là 1 mới cho phép cập nhật
            return jsonify({"status": "error", "message": "Bạn không có quyền thêm mới chi bộ."}), 403

        try:
            self.cur = self.con.cursor(dictionary=True)
            data = request.get_json()
            if not data:
                return json.dumps({"status": "error", "message": "Dữ liệu JSON không hợp lệ"}, ensure_ascii=False), 400
            

            sql_chibo = """
            INSERT INTO quanlydangvien.chibo (TenChiBo, TenVietTatChiBo, GhiChuChiBo)
            VALUES (%s, %s, %s)
            """
            values_chibo = (
               data["TenChiBo"], data["TenVietTatChiBo"], data.get("GhiChuChiBo")
            )
            self.cur.execute(sql_chibo, values_chibo)
            self.con.commit()

            response = {
                "status": "success",
                "message": "Chi bộ được tạo thành công",
                "chibo": {
                    "TenChiBo": data["TenChiBo"],
                    "TenVietTatChiBo": data["TenVietTatChiBo"],
                    "GhiChuChiBo": data.get("GhiChuChiBo")
                }
            }
            return json.dumps(response, ensure_ascii=False), 201

        except mysql.connector.Error as err:
            self.con.rollback()
            return json.dumps({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}, ensure_ascii=False), 500

        except Exception as e:
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400

        finally:
            self.cur.close()

    def chibo_getall_model(self):
        try:
            # Kiểm tra nếu kết nối MySQL đã được thiết lập
            if not hasattr(self, 'con') or not self.con.is_connected():
                raise Exception("Kết nối cơ sở dữ liệu đã bị đóng hoặc không hợp lệ.")

            # Sử dụng with statement để tự động đóng cursor
            with self.con.cursor(dictionary=True) as cur:
                # Truy vấn loại bỏ chi bộ có mã là 999
                sql = "SELECT * FROM chibo WHERE MaChiBo != 999"
                cur.execute(sql)
                result = cur.fetchall()

                # Trả kết quả dưới dạng JSON
                return jsonify({"status": "success", "data": result}), 200

        except mysql.connector.Error as err:
            # Bắt lỗi MySQL
            return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500

        except AttributeError:
            # Lỗi khi self.con chưa được khởi tạo
            return jsonify({"status": "error", "message": "Lỗi: Kết nối MySQL chưa được thiết lập."}), 500

        except Exception as e:
            # Bắt lỗi chung
            return jsonify({"status": "error", "message": f"Lỗi: {str(e)}"}), 500


