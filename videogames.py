from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, send_file
import sqlite3
from model import Articolo, Gioco
import os

games = Blueprint("games", __name__, template_folder="templates", static_folder="static")
default_path = "./static/uploads/games/"


@games.route("/")
def index():
    if request.args.get("filename"):
        return redirect(url_for("games.download", filename=request.args.get("filename")))
    else:
        data=Gioco.query.all()
        if "username" in session:
            return render_template("games.html", data=data, name=session["username"])
        else:
            return render_template("games.html", data=data, name="")

@games.route("/download/<filename>")
def download(filename):
    g=Gioco.query.filter_by(nome_file=filename).first()
    return send_file(os.path.join(default_path, filename), as_attachment=True)
