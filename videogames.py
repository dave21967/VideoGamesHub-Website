from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, send_file
import mysql.connector as mysql
from model import Articolo
import os

mysql_user = "root"
mysql_password = None

games = Blueprint("games", __name__, template_folder="templates", static_folder="static")
default_path = "./static/uploads/games/"


@games.route("/")
def index():
    if request.args.get("filename"):
        return redirect(url_for("games.download", filename=request.args.get("filename")))
    else:
        files=os.listdir("./VideogamesHub Website/static/uploads/games/")
        return render_template("games.html", data=files)

@games.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(default_path, filename), as_attachment=True)