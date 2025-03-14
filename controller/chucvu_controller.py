from app import app
from model.chucvu_model import chucvu_model
from flask import request

object = chucvu_model()

@app.route("/chucvu/getall")
def chucvu_getall_controller():
    return object.chucvu_getall_model()

@app.route("/chucvu/add", methods=["POST"])
def add_chucvu():
    model = chucvu_model()
    return model.chucvu_add_model(request)

@app.route("/chucvu/delete/<id>", methods=["DELETE"])
def chucvu_delete_controller(id):
    return object.chucvu_delete_model(id)

@app.route("/chucvu/update/<MaChucVu>", methods = ["PUT"])
def chucvu_update_controller(MaChucVu):
    return object.chucvu_update_model(MaChucVu, request)