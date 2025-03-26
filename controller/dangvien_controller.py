import json
from app import app
from model.dangvien_model import dangvien_model
from flask import request

object = dangvien_model()


@app.route("/dangvien/getall")
def dangvien_getall_controller():
    return object.dangvien_getall_model()

@app.route("/dangvien/getall/trongdangbo")
def dangvien_getall_trongdangbo_controller():
    return object.dangvien_getall_trongdangbo_model()

@app.route("/dangvien/add", methods=["POST"])
def add_dangvien():
    model = dangvien_model()
    return model.dangvien_add_model(request)

@app.route("/dangvien/updateThongTin/<SoTheDangVien>", methods = ["PUT"])
def dangvien_updateThongTin_controller(SoTheDangVien):
    return object.dangvien_updateThongTin_model(SoTheDangVien, request)

@app.route("/dangvien/chuyenCongTacTrong/<SoTheDangVien>", methods = ["PUT"])
def dangvien_chuyenCongTacTrong_controller(SoTheDangVien):
    return object.dangvien_chuyenCongTacTrong_model(SoTheDangVien, request)

@app.route("/dangvien/timKiem", methods=["POST"])
def dangvien_timKiem_controller():
    return object.dangvien_timkiem_model(request)

@app.route("/dangvien/delete/<id>", methods = ["DELETE"])
def dangvien_delete_controller(id):
    return object.dangvien_delete_model(id)

@app.route("/dangvien/getall/ngoaidangbo")
def dangvien_getall_ngoaidangbo_controller():
    return object.dangvien_getall_ngoaidangbo_model()


@app.route("/dangvien/timKiem/ngoaidangbo", methods=["POST"])
def dangvien_timkiem_ngoaidangbo_controller():
    return object.dangvien_timkiem_ngoaidangbo_model(request)

@app.route("/dangvien/xoaTheoNgay", methods=["DELETE"])
def dangvien_xoaTheoNgay_controller():
    try:
        # Lấy dữ liệu từ request body (JSON)
        data = request.get_json()
        ngay_xoa = data.get("ngayXoa")  # Dữ liệu phải có dạng {"ngayXoa": "yyyy-MM-dd"}

        if not ngay_xoa:
            return json.dumps({"status": "error", "message": "Thiếu ngày xóa!"}, ensure_ascii=False), 400

        # Gọi model để xử lý
        return object.dangvien_delete_by_date(ngay_xoa)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Lỗi không xác định: {str(e)}"}, ensure_ascii=False), 500
