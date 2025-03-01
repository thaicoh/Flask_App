from app import app
from model.dangvien_model import dangvien_model
from flask import request

object = dangvien_model()


@app.route("/dangvien/getall")
def dangvien_getall_controller():
    return object.dangvien_getall_model()

@app.route("/dangvien/add", methods=["POST"])
def add_dangvien():
    model = dangvien_model()
    return model.dangvien_add_model(request)

@app.route("/dangvien/update/<SoTheDangVien>", methods = ["PUT"])
def dangvien_update_controller(SoTheDangVien):
    return object.dangvien_update_model(SoTheDangVien, request)
