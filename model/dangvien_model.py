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

required_fields_add = [
        "SoTheDangVien", "SoLyLich", "HoVaTenKhaisinh", "GioiTinh", "QueQuan", 
        "NoiDangKyHoKhau", "DanToc", "NgayVaoDang", "NgaySinh", "ChiBoNgayVaoDang", 
        "NgayVaoDangChinhThuc", "ChiBoNgayVaoDangChinhThuc", "HocVanPhoThong", 
        "ChuyenMonNghiepVu", "LyLuanChinhTri", "HocHam", "HocVi", "NgoaiNgu", 
        "SoCCCD", "KhenThuong", "HuyHieuDang", "MaChucVu", "NoiSinh", "MaChiBo", 
        "NgayBatDau", "LyDo"
    ]

required_fields_update = [
        "SoLyLich", "HoVaTenKhaisinh", "GioiTinh", "QueQuan", 
        "NoiDangKyHoKhau", "DanToc", "NgayVaoDang", "NgaySinh", "ChiBoNgayVaoDang", 
        "NgayVaoDangChinhThuc", "ChiBoNgayVaoDangChinhThuc", "HocVanPhoThong", 
        "ChuyenMonNghiepVu", "LyLuanChinhTri", "HocHam", "HocVi", "NgoaiNgu", 
        "SoCCCD", "KhenThuong", "HuyHieuDang", "MaChucVu", "NoiSinh", "MaChiBo", 
        "NgayBatDau", "LyDo"
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

    @token_required
    def dangvien_update_model(self, SoTheDangVien, request):
        print("SoTheDangVien:" , SoTheDangVien)

        data = request.get_json()
        print("Dữ liệu JSON nhận được:", data)

        try:
            self.cur = self.con.cursor(dictionary=True)
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "Dữ liệu JSON không hợp lệ"}), 400
            
            is_valid, message = validate_data(data, required_fields_update)
            if not is_valid:
                return jsonify({"status": "error", "message": message}), 400

            # Kiểm tra xem đảng viên có tồn tại không
            self.cur.execute("SELECT * FROM quanlydangvien.dangvien WHERE SoTheDangVien = %s", (SoTheDangVien,))
            existing_dangvien = self.cur.fetchone()
            if not existing_dangvien:
                return jsonify({"status": "error", "message": "Không tìm thấy đảng viên"}), 404

            # Cập nhật bảng dangvien
            sql_dangvien = """
            UPDATE quanlydangvien.dangvien 
            SET SoLyLich=%s, HoVaTenKhaisinh=%s, GioiTinh=%s, QueQuan=%s, NoiDangKyHoKhau=%s, DanToc=%s, NgayVaoDang=%s, NgaySinh=%s, 
                ChiBoNgayVaoDang=%s, NgayVaoDangChinhThuc=%s, ChiBoNgayVaoDangChinhThuc=%s, HocVanPhoThong=%s, ChuyenMonNghiepVu=%s, 
                LyLuanChinhTri=%s, HocHam=%s, HocVi=%s, NgoaiNgu=%s, SoCCCD=%s, KhenThuong=%s, HuyHieuDang=%s, MaChucVu=%s, NoiSinh=%s
            WHERE SoTheDangVien=%s
            """
            values_dangvien = (
                data["SoLyLich"], data["HoVaTenKhaisinh"], data["GioiTinh"], data["QueQuan"], 
                data["NoiDangKyHoKhau"], data["DanToc"], data["NgayVaoDang"], data["NgaySinh"], 
                data["ChiBoNgayVaoDang"], data["NgayVaoDangChinhThuc"], data["ChiBoNgayVaoDangChinhThuc"], 
                data["HocVanPhoThong"], data["ChuyenMonNghiepVu"], data["LyLuanChinhTri"], data["HocHam"], 
                data["HocVi"], data["NgoaiNgu"], data["SoCCCD"], data["KhenThuong"], data["HuyHieuDang"], 
                data["MaChucVu"], data["NoiSinh"], SoTheDangVien
            )
            self.cur.execute(sql_dangvien, values_dangvien)

            # Cập nhật bảng lịch sử công tác (nếu có dữ liệu)
            if "MaChiBo" in data and "NgayBatDau" in data:
                sql_lichsucongtac = """
                UPDATE quanlydangvien.lichsucongtac 
                SET MaChiBo=%s, NgayBatDau=%s, NgayKetThuc=%s, LyDo=%s
                WHERE SoTheDangVien=%s
                """
                ngay_ket_thuc = data.get("NgayKetThuc")
                if not ngay_ket_thuc:  # Nếu không có hoặc là "", gán None
                    ngay_ket_thuc = None  

                values_lichsucongtac = (
                    data["MaChiBo"], data["NgayBatDau"], ngay_ket_thuc, data.get("LyDo", ""), SoTheDangVien
                )
                self.cur.execute(sql_lichsucongtac, values_lichsucongtac)

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
    def dangvien_getall_model(self):
        try:
            self.cur = self.con.cursor(dictionary=True)
            sql = "SELECT * FROM quanlydangvien.dangvien"
            self.cur.execute(sql)
            result = self.cur.fetchall()

            return jsonify({"status": "success", "data": result}), 200
        
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Lỗi cơ sở dữ liệu: {str(err)}"}), 500
        
        finally:
            self.cur.close()

    @token_required
    def dangvien_add_model(self, request):

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
                                                LyLuanChinhTri, HocHam, HocVi, NgoaiNgu, SoCCCD, KhenThuong, HuyHieuDang, MaChucVu, NoiSinh) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values_dangvien = (
                data["SoTheDangVien"], data["SoLyLich"], data["HoVaTenKhaisinh"], data["GioiTinh"], data["QueQuan"], 
                data["NoiDangKyHoKhau"], data["DanToc"], data["NgayVaoDang"], data["NgaySinh"], data["ChiBoNgayVaoDang"], 
                data["NgayVaoDangChinhThuc"], data["ChiBoNgayVaoDangChinhThuc"], data["HocVanPhoThong"], 
                data["ChuyenMonNghiepVu"], data["LyLuanChinhTri"], data["HocHam"], data["HocVi"], data["NgoaiNgu"], 
                data["SoCCCD"], data["KhenThuong"], data["HuyHieuDang"], data["MaChucVu"], data["NoiSinh"]
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
