from app import app
from model.user_model import user_model
from flask import request

from utils.auth import token_required
obj = user_model()

@app.route("/user/getall")
def user_getall_controller():
    return obj.user_getall_model()

@app.route("/user/addone", methods = ["POST"])
def user_addone_controller():
    return obj.user_addone_model(request.form)

@app.route("/user/update", methods = ["PUT"])
def user_update_controller():   
    data = request.get_json()
    return obj.user_update_model(data)

@app.route("/user/delete/<id>", methods = ["DELETE"])
def user_delete_controller(id):
    return obj.user_delete_model(id)

@app.route("/user/login", methods = ["POST"])
def user_login_controller():
    data = request.get_json()
    return obj.user_login_model(data)

@app.route("/user/getinfo/<int:id>", methods=["GET"])
@token_required
def user_getinfo_controller(id):
    return obj.user_getinfo_model(id)

