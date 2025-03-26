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


required_fields_add = [
        "SoTheDangVien", "HoVaTenKhaisinh", "GioiTinh", "QueQuan", 
        "NgayVaoDang", "NgaySinh",
        "NgayVaoDangChinhThuc", 
        "LyLuanChinhTri", "MaChucVu", "MaChiBo", 
        "NgayBatDau"
    ]


def validate_data(data, required_fields):

    # Kiểm tra trường thiếu
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return False, f"Thiếu dữ liệu trường: {', '.join(missing_fields)}"


    # Kiểm tra MaChiBo là số nguyên
    try:
        data["MaChiBo"] = int(data["MaChiBo"])
    except ValueError:
        return False, "MaChiBo phải là số nguyên"

    # Kiểm tra định dạng ngày tháng hợp lệ
    date_fields = ["NgayVaoDang", "NgaySinh", "NgayBatDau"]
    for field in date_fields:
        try:
            datetime.datetime.strptime(data[field], "%Y-%m-%d")
        except ValueError:
            return False, f"Trường {field} không đúng định dạng YYYY-MM-DD"

    return True, "Dữ liệu hợp lệ"

class dangvien_model:
    def __init__(self):
        db = Database()
        self.con, self.cur = db.get_connection()


    def dangvien_getall_ngoaidangbo_model(self):
        try:
            self.cur = self.con.cursor(dictionary=True)
            sql = "SELECT * FROM dangvien WHERE MaChiBo = 999"
            self.cur.execute(sql)
            result = self.cur.fetchall()

            # Duyệt qua từng bản ghi trong kết quả và chuyển đổi các trường ngày tháng về định dạng yyyy-mm-dd
            for item in result:
                if 'NgaySinh' in item and item['NgaySinh']:
                    item['NgaySinh'] = item['NgaySinh'].strftime('%Y-%m-%d')
                if 'NgayVaoDang' in item and item['NgayVaoDang']:
                    item['NgayVaoDang'] = item['NgayVaoDang'].strftime('%Y-%m-%d')
                if 'NgayVaoDangChinhThuc' in item and item['NgayVaoDangChinhThuc']:
                    item['NgayVaoDangChinhThuc'] = item['NgayVaoDangChinhThuc'].strftime('%Y-%m-%d')

            return jsonify({"status": "success", "data": result}), 200
        
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500
        
        finally:
            self.cur.close()


    @token_required
    def dangvien_timkiem_ngoaidangbo_model(self, request):
        try:
            self.cur = self.con.cursor(dictionary=True)
            data = request.get_json()
            
            if not data:
                return json.dumps({"status": "error", "message": "Dữ liệu JSON không hợp lệ"}, ensure_ascii=False), 400
            
            search_string = data.get("search_string", "").strip()
            MaChiBo = 999
            MaChucVu = data.get("MaChucVu")
            
            # Truy vấn trực tiếp từ bảng dangvien
            query_dangvien = "SELECT * FROM quanlydangvien.dangvien WHERE 1=1"  # 1=1 để dễ thêm điều kiện
            values = []
            
            if search_string:
                query_dangvien += " AND (SoTheDangVien LIKE %s OR SoLyLich LIKE %s OR HoVaTenKhaiSinh LIKE %s OR SoCCCD LIKE %s)"
                values.extend([f"%{search_string}%"] * 4)
            
            if MaChiBo is not None:  # Kiểm tra cả giá trị 0
                query_dangvien += " AND MaChiBo = %s"
                values.append(MaChiBo)
            
            if MaChucVu is not None:  # Kiểm tra cả giá trị 0
                query_dangvien += " AND MaChucVu = %s"
                values.append(MaChucVu)
            
            self.cur.execute(query_dangvien, tuple(values))
            result = self.cur.fetchall()
            
            if not result:
                return json.dumps({"status": "success", "message": "Không có kết quả phù hợp", "data": []}, ensure_ascii=False), 200
            
            # Chuyển đổi kiểu date thành string
            for row in result:
                for key, value in row.items():
                    if isinstance(value, datetime.date):
                        row[key] = value.strftime("%Y-%m-%d")
            
            return json.dumps({
                "status": "success",
                "message": "Tìm kiếm thành công",
                "data": result
            }, ensure_ascii=False), 200
        
        except mysql.connector.Error as err:
            return json.dumps({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}, ensure_ascii=False), 500
        
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400
        
        finally:
            self.cur.close()

    @token_required
    def dangvien_chuyenCongTacTrong_model(self, SoTheDangVien, request):
        print("SoTheDangVien:", SoTheDangVien)

        data = request.get_json()
        print("Dữ liệu JSON nhận được:", data)

        user_role = request.vaitro
        if user_role != 1:
            return jsonify({"status": "error", "message": "Bạn không có quyền cập nhật dữ liệu."}), 403

        try:
            self.cur = self.con.cursor(dictionary=True)

            # Kiểm tra đảng viên có tồn tại không
            self.cur.execute("SELECT MaChiBo FROM quanlydangvien.dangvien WHERE SoTheDangVien = %s", (SoTheDangVien,))
            existing_dangvien = self.cur.fetchone()
            if not existing_dangvien:
                return jsonify({"status": "error", "message": "Không tìm thấy đảng viên"}), 404

            new_ma_chi_bo = data.get("MaChiBo")

            # Cập nhật MaChiBo trong bảng dangvien
            sql = "UPDATE quanlydangvien.dangvien SET MaChiBo = %s WHERE SoTheDangVien = %s"
            self.cur.execute(sql, (new_ma_chi_bo, SoTheDangVien))

            # Tạo một con trỏ mới để tránh lỗi "Unread result found"
            temp_cursor = self.con.cursor(dictionary=True)

            # Lấy lịch sử công tác gần nhất với NgayKetThuc = NULL
            temp_cursor.execute("""
                SELECT * FROM quanlydangvien.lichsucongtac 
                WHERE SoTheDangVien = %s AND NgayKetThuc IS NULL
                ORDER BY NgayBatDau DESC LIMIT 1
            """, (SoTheDangVien,))
            current_lich_su = temp_cursor.fetchone()  # Lấy bản ghi gần nhất

            if current_lich_su:
                # Chuyển current_lich_su["NgayBatDau"] thành chuỗi để so sánh
                ngay_bat_dau_db = current_lich_su["NgayBatDau"].strftime("%Y-%m-%d")
                print("NgayBatDau == data.NgayBatDau : ", ngay_bat_dau_db, "  ", data["NgayBatDau"])

                # Kiểm tra nếu NgayBatDau của lịch sử gần nhất khớp với ngày gửi lên
                if ngay_bat_dau_db == data["NgayBatDau"]:
                    print("NgayBatDau == data.NgayBatDau : " ,ngay_bat_dau_db , "  ",  data["NgayBatDau"])

                    print("Chỉ cập nhật MaChiBo và LyDo trong lịch sử công tác hiện tại")
                    # Chỉ cập nhật MaChiBo và LyDo trong lịch sử công tác hiện tại
                    sql_update_lichsu = """
                        UPDATE quanlydangvien.lichsucongtac 
                        SET MaChiBo = %s, LyDo = %s
                        WHERE SoTheDangVien = %s AND NgayKetThuc IS NULL AND NgayBatDau = %s
                    """
                    self.cur.execute(sql_update_lichsu, (new_ma_chi_bo, data["LyDo"], SoTheDangVien, data["NgayBatDau"]))
                else:
                    print("NgayBatDau == data.NgayBatDau : " ,ngay_bat_dau_db , "  ",  data["NgayBatDau"])
                    print("Nếu không khớp, cập nhật NgayKetThuc cho lịch sử công tác hiện tại")
                    # Nếu không khớp, cập nhật NgayKetThuc cho lịch sử công tác hiện tại
                    sql_update_lichsu = """
                        UPDATE quanlydangvien.lichsucongtac 
                        SET NgayKetThuc = %s 
                        WHERE SoTheDangVien = %s AND NgayKetThuc IS NULL
                    """
                    self.cur.execute(sql_update_lichsu, (data["NgayBatDau"], SoTheDangVien))

                    # Thêm mới lịch sử công tác
                    sql_lichsucongtac = """
                        INSERT INTO quanlydangvien.lichsucongtac (SoTheDangVien, MaChiBo, NgayBatDau, NgayKetThuc, LyDo) 
                        VALUES (%s, %s, %s, NULL, %s)
                    """
                    values_lichsucongtac = (
                        SoTheDangVien, new_ma_chi_bo, data["NgayBatDau"], data["LyDo"]
                    )
                    self.cur.execute(sql_lichsucongtac, values_lichsucongtac)
            else:
                # Nếu không có lịch sử công tác nào, thêm mới
                sql_lichsucongtac = """
                    INSERT INTO quanlydangvien.lichsucongtac (SoTheDangVien, MaChiBo, NgayBatDau, NgayKetThuc, LyDo) 
                    VALUES (%s, %s, %s, NULL, %s)
                """
                values_lichsucongtac = (
                    SoTheDangVien, new_ma_chi_bo, data["NgayBatDau"], data["LyDo"]
                )
                self.cur.execute(sql_lichsucongtac, values_lichsucongtac)

            self.con.commit()

            response = {
                "status": "success",
                "message": "Cập nhật MaChiBo và lịch sử công tác thành công.",
                "dangvien": {
                    "SoTheDangVien": SoTheDangVien,
                    "NgayBatDau": data["NgayBatDau"],
                    "MaChiBo": new_ma_chi_bo
                }
            }
            return json.dumps(response, ensure_ascii=False), 201

        except Exception as e:
            self.con.rollback()
            return jsonify({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}), 400

        finally:
            self.cur.close()
            if 'temp_cursor' in locals():
                temp_cursor.close()

    @token_required
    def dangvien_timkiem_model(self, request):
        try:
            data = request.get_json()
            
            if not data:
                return json.dumps({"status": "error", "message": "Dữ liệu JSON không hợp lệ"}, ensure_ascii=False), 400
            
            search_string = data.get("search_string", "").strip()
            MaChiBo = data.get("MaChiBo")
            MaChucVu = data.get("MaChucVu")
            NgayTimKiem = data.get("NgayTimKiem")
            
            if not NgayTimKiem:
                return json.dumps({"status": "error", "message": "Thiếu ngày tìm kiếm"}, ensure_ascii=False), 400
            
            try:
                NgayTimKiem = datetime.datetime.strptime(NgayTimKiem, "%Y-%m-%d").date()
            except ValueError:
                return json.dumps({"status": "error", "message": "Định dạng ngày không hợp lệ, yêu cầu YYYY-MM-DD"}, ensure_ascii=False), 400
            
            # 🔹 Tạo kết nối mới cho từng truy vấn
            with self.con.cursor(dictionary=True) as cur:
                # Truy vấn danh sách SoTheDangVien hợp lệ
                query_lichsu = """
                    SELECT SoTheDangVien, MaChiBo, MaLichSu AS MaLichSuCongTac, LyDo
                    FROM quanlydangvien.lichsucongtac 
                    WHERE NgayBatDau <= %s 
                    AND (NgayKetThuc > %s OR NgayKetThuc IS NULL) 
                    AND MaChiBo != 999
                """
                values = [NgayTimKiem, NgayTimKiem]
                if MaChiBo:
                    query_lichsu += " AND MaChiBo = %s"
                    values.append(MaChiBo)
                
                query_lichsu += " ORDER BY NgayBatDau DESC"
                
                cur.execute(query_lichsu, tuple(values))
                result_lichsu = cur.fetchall()
            
            # Xử lý kết quả truy vấn
            danh_sach_ma_dang_vien = []
            lich_su_mapping = {}
            for row in result_lichsu:
                so_the = row["SoTheDangVien"]
                if so_the not in lich_su_mapping:
                    danh_sach_ma_dang_vien.append(so_the)
                    lich_su_mapping[so_the] = {
                        "MaChiBo": row["MaChiBo"],
                        "MaLichSuCongTac": row["MaLichSuCongTac"],
                        "LyDo": row["LyDo"]
                    }
            
            if not danh_sach_ma_dang_vien:
                return json.dumps({"status": "success", "message": "Không có kết quả phù hợp", "data": []}, ensure_ascii=False), 200
            
            # 🔹 Tạo kết nối mới cho truy vấn thứ hai
            with self.con.cursor(dictionary=True) as cur:
                # Truy vấn danh sách đảng viên
                query_dangvien = """
                    SELECT * FROM quanlydangvien.dangvien 
                    WHERE SoTheDangVien IN (%s)
                """ % (",".join(["%s"] * len(danh_sach_ma_dang_vien)))
                
                values = list(danh_sach_ma_dang_vien)
                
                if search_string:
                    query_dangvien += " AND (SoTheDangVien LIKE %s OR SoLyLich LIKE %s OR HoVaTenKhaiSinh LIKE %s OR SoCCCD LIKE %s)"
                    values.extend([f"%{search_string}%"] * 4)
                
                if MaChucVu:
                    query_dangvien += " AND MaChucVu = %s"
                    values.append(MaChucVu)
                
                cur.execute(query_dangvien, tuple(values))
                result = cur.fetchall()
            
            # Chuyển đổi kiểu date và thêm thông tin từ lichsucongtac
            for row in result:
                so_the = row["SoTheDangVien"]
                lich_su = lich_su_mapping.get(so_the, {})
                row["MaChiBoNgayTimKiem"] = lich_su.get("MaChiBo", None)
                row["MaLichSuCongTac"] = lich_su.get("MaLichSuCongTac", None)
                row["LyDo"] = lich_su.get("LyDo", None)
                
                for key, value in row.items():
                    if isinstance(value, datetime.date):
                        row[key] = value.strftime("%Y-%m-%d")
            
            return json.dumps({
                "status": "success",
                "message": "Tìm kiếm thành công",
                "data": result
            }, ensure_ascii=False), 200
        
        except mysql.connector.Error as err:
            return json.dumps({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}, ensure_ascii=False), 500
        
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400




    @token_required
    def dangvien_updateThongTin_model(self, SoTheDangVien, request):
        print("SoTheDangVien:", SoTheDangVien)

        data = request.get_json()
        print("Dữ liệu JSON nhận được:", data)

        user_role = request.vaitro
        if user_role != 1:
            return jsonify({"status": "error", "message": "Bạn không có quyền cập nhật dữ liệu."}), 403
        
        try:
            self.cur = self.con.cursor(dictionary=True)

            # Kiểm tra đảng viên có tồn tại không
            self.cur.execute("SELECT * FROM quanlydangvien.dangvien WHERE SoTheDangVien = %s", (SoTheDangVien,))
            existing_dangvien = self.cur.fetchone()
            if not existing_dangvien:
                return jsonify({"status": "error", "message": "Không tìm thấy đảng viên"}), 404

            
            # Chỉ cập nhật các trường có trong request
            update_fields = []
            values = []
            for field in data:
                if field in existing_dangvien:  # Chỉ cập nhật nếu trường tồn tại
                    update_fields.append(f"{field} = %s")
                    values.append(data[field])

            if not update_fields:
                return jsonify({"status": "error", "message": "Không có dữ liệu nào để cập nhật"}), 400

            values.append(SoTheDangVien)
            sql = f"UPDATE quanlydangvien.dangvien SET {', '.join(update_fields)} WHERE SoTheDangVien = %s"
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

    def dangvien_getall_model(self):
        try:
            self.cur = self.con.cursor(dictionary=True)
            sql = "SELECT * FROM dangvien"
            self.cur.execute(sql)
            result = self.cur.fetchall()

            return jsonify({"status": "success", "data": result}), 200
        
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500
        
        finally:
            self.cur.close()

    def dangvien_getall_trongdangbo_model(self):
        try:
            self.cur = self.con.cursor(dictionary=True)
            
            # Thêm điều kiện WHERE để loại bỏ đảng viên có MaChiBo là 999
            sql = "SELECT * FROM dangvien WHERE MaChiBo != 999"
            
            self.cur.execute(sql)
            result = self.cur.fetchall()

            return jsonify({"status": "success", "data": result}), 200
        
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500
        
        finally:
            self.cur.close()

    @token_required
    def dangvien_add_model(self, request):

        # Lấy vai trò từ request
        user_role = request.vaitro
        print("Vai trò người dùng:", user_role)  # Debug

        # Kiểm tra vai trò trước khi thực hiện cập nhật
        if user_role != 1 :  # Nếu VaiTro là 1 mới cho phép cập nhật
            return jsonify({"status": "error", "message": "Bạn không có quyền thêm mới đảng viên."}), 403


        try:
            self.cur = self.con.cursor(dictionary=True)
            data = request.get_json()
            if not data:
                return json.dumps({"status": "error", "message": "Dữ liệu JSON không hợp lệ"}, ensure_ascii=False), 400
            
            is_valid, message = validate_data(data, required_fields_add)
            if not is_valid:
                return json.dumps({"status": "error", "message": message}, ensure_ascii=False), 400

            sql_dangvien = """
            INSERT INTO quanlydangvien.dangvien (SoTheDangVien, SoLyLich, HoVaTenKhaisinh, GioiTinh, QueQuan, NoiDangKyHoKhau, DanToc, NgayVaoDang, NgaySinh, 
                                                ChiBoNgayVaoDang, NgayVaoDangChinhThuc, ChiBoNgayVaoDangChinhThuc, HocVanPhoThong, ChuyenMonNghiepVu, 
                                                LyLuanChinhTri, HocHam, HocVi, NgoaiNgu, SoCCCD, KhenThuong, HuyHieuDang, MaChucVu, NoiSinh, MaChiBo, TonGiao, QHTPP, QHDUVP) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values_dangvien = (
                data["SoTheDangVien"], data["SoLyLich"], data["HoVaTenKhaisinh"], data["GioiTinh"], data["QueQuan"], 
                data["NoiDangKyHoKhau"], data["DanToc"], data["NgayVaoDang"], data["NgaySinh"], data["ChiBoNgayVaoDang"], 
                data["NgayVaoDangChinhThuc"], data["ChiBoNgayVaoDangChinhThuc"], data["HocVanPhoThong"], 
                data["ChuyenMonNghiepVu"], data["LyLuanChinhTri"], data["HocHam"], data["HocVi"], data["NgoaiNgu"], 
                data["SoCCCD"], data["KhenThuong"], data["HuyHieuDang"], data["MaChucVu"], data["NoiSinh"], data["MaChiBo"], data["TonGiao"], data["QHTPP"], data["QHDUVP"]
            )
            self.cur.execute(sql_dangvien, values_dangvien)

            sql_lichsucongtac = """
            INSERT INTO quanlydangvien.lichsucongtac (SoTheDangVien, MaChiBo, NgayBatDau, NgayKetThuc, LyDo) 
            VALUES (%s, %s, %s, %s, %s)
            """

            # Xử lý NgayKetThuc: Nếu không có hoặc là "", gán None
            ngay_ket_thuc = data.get("NgayKetThuc")
            if not ngay_ket_thuc:  # Trường hợp None hoặc ""
                ngay_ket_thuc = None  

            values_lichsucongtac = (
                data["SoTheDangVien"], data["MaChiBo"], data["NgayBatDau"], ngay_ket_thuc, data["LyDo"]
            )
            self.cur.execute(sql_lichsucongtac, values_lichsucongtac)

            self.con.commit()

            response = {
                "status": "success",
                "message": "Đảng viên và lịch sử công tác được tạo thành công",
                "dangvien": {
                    "SoTheDangVien": data["SoTheDangVien"],
                    "HoVaTenKhaisinh": data["HoVaTenKhaisinh"],
                    "NgayVaoDang": data["NgayVaoDang"],
                    "MaChiBo": data["MaChiBo"]
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

    @token_required
    def dangvien_delete_model(self, id):
        try:
            self.cur = self.con.cursor(dictionary=True)  # Tạo cursor mới tránh cache

            # 🔹 **1. Lấy user_id từ request (middleware đã kiểm tra token)**
            user_id = request.user_id
            print("User ID từ token:", user_id)  # Debug xem user_id có đúng không

            # 🔹 **2. Kiểm tra quyền (chỉ admin - vai trò 1 - mới được xóa)**
            self.cur.execute("SELECT VaiTro FROM nguoidung WHERE MaNguoiDung = %s", (user_id,))
            user = self.cur.fetchone()

            if not user or user["VaiTro"] != 1:
                return json.dumps({"status": "error", "message": "Bạn không có quyền xóa đảng viên!"}, ensure_ascii=False), 403

            # 🔹 **3. Xóa tất cả bản ghi trong lichsucongtac liên quan đến SoTheDangVien**
            sql_lichsu = "DELETE FROM quanlydangvien.lichsucongtac WHERE SoTheDangVien = %s"
            self.cur.execute(sql_lichsu, (id,))
            print(f"Đã xóa {self.cur.rowcount} bản ghi trong lichsucongtac")  # Debug số dòng bị xóa

            # 🔹 **4. Tiến hành xóa đảng viên**
            sql_dangvien = "DELETE FROM quanlydangvien.dangvien WHERE SoTheDangVien = %s"
            self.cur.execute(sql_dangvien, (id,))

            # Kiểm tra số dòng bị ảnh hưởng trong bảng dangvien
            if self.cur.rowcount > 0:
                self.con.commit()  # Xác nhận xóa cả hai bảng
                return json.dumps({"status": "success", "message": "Xóa đảng viên và lịch sử công tác thành công!", "deleted_id": id}, ensure_ascii=False), 200
            else:
                self.con.rollback()  # Hoàn tác nếu không xóa được đảng viên
                return json.dumps({"status": "error", "message": "Không tìm thấy đảng viên để xóa.", "deleted_id": id}, ensure_ascii=False), 404

        except mysql.connector.Error as err:
            self.con.rollback()  # Hoàn tác nếu có lỗi cơ sở dữ liệu
            return json.dumps({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}, ensure_ascii=False), 500

        except Exception as e:
            self.con.rollback()  # Hoàn tác nếu có lỗi không xác định
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400

        finally:
            self.cur.close()  # Đóng cursor


    @token_required
    def dangvien_delete_by_date(self, ngay_xoa):
        try:
            self.cur = self.con.cursor(dictionary=True)

            # 🔹 **1. Kiểm tra quyền người dùng**
            user_id = request.user_id
            self.cur.execute("SELECT VaiTro FROM nguoidung WHERE MaNguoiDung = %s", (user_id,))
            user = self.cur.fetchone()

            if not user or user["VaiTro"] != 1:
                return json.dumps({"status": "error", "message": "Bạn không có quyền xóa đảng viên!"}, ensure_ascii=False), 403

            print(f"🔍 Ngày cần xóa: {ngay_xoa}")

            # 🔹 **2. Tìm danh sách đảng viên cần xóa**
            sql_find_dangvien = """
            SELECT SoTheDangVien FROM quanlydangvien.lichsucongtac 
            WHERE NgayBatDau = %s AND NgayKetThuc IS NULL AND LyDo = %s
            """

            ly_do = f"Thêm mới từ file excel ngày {ngay_xoa}"  # Format lý do

            self.cur.execute(sql_find_dangvien, (ngay_xoa, ly_do))
            danh_sach_dangvien = self.cur.fetchall()

            if not danh_sach_dangvien:
                return json.dumps({"status": "error", "message": "Không có đảng viên nào cần xóa theo ngày này."}, ensure_ascii=False), 404

            ds_so_the = [dv["SoTheDangVien"] for dv in danh_sach_dangvien]
            print(f"📌 Danh sách đảng viên cần xóa: {ds_so_the}")

            # 🔹 **3. Xóa lịch sử công tác trước**
            sql_delete_lichsu = f"""
            DELETE FROM quanlydangvien.lichsucongtac 
            WHERE SoTheDangVien IN ({','.join(['%s'] * len(ds_so_the))})
            """
            self.cur.execute(sql_delete_lichsu, tuple(ds_so_the))
            print(f"🗑 Đã xóa {self.cur.rowcount} bản ghi trong lichsucongtac.")

            # 🔹 **4. Sau khi xóa lịch sử công tác, mới xóa đảng viên**
            sql_delete_dangvien = f"""
            DELETE FROM quanlydangvien.dangvien 
            WHERE SoTheDangVien IN ({','.join(['%s'] * len(ds_so_the))})
            """
            self.cur.execute(sql_delete_dangvien, tuple(ds_so_the))
            print(f"🗑 Đã xóa {self.cur.rowcount} bản ghi trong dangvien.")

            if self.cur.rowcount > 0:
                self.con.commit()
                return json.dumps({"status": "success", "message": f"Xóa {len(ds_so_the)} đảng viên thành công!", "deleted_ids": ds_so_the}, ensure_ascii=False), 200
            else:
                self.con.rollback()
                return json.dumps({"status": "error", "message": "Không thể xóa đảng viên."}, ensure_ascii=False), 500

        except mysql.connector.Error as err:
            self.con.rollback()
            return json.dumps({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}, ensure_ascii=False), 500

        except Exception as e:
            self.con.rollback()
            return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 400

        finally:
            self.cur.close()


