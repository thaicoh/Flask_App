from app import app
from model.chibo_model import chibo_model
from flask import request

object = chibo_model()

@app.route("/chibo/getall")
def chibo_getall_controller():
    return object.chibo_getall_model()

@app.route("/chibo/add", methods=["POST"])
def add_chibo():
    model = chibo_model()
    return model.chibo_add_model(request)

@app.route("/chibo/delete/<id>", methods = ["DELETE"])
def chibo_delete_controller(id):
    return object.chibo_delete_model(id)

@app.route("/chibo/update/<MaChiBo>", methods = ["PUT"])
def chibo_update_controller(MaChiBo):
    return object.chibo_update_model(MaChiBo, request)