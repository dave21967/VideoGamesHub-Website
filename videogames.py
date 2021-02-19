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
        files=os.listdir(current_app.config["GAMES-UPLOADS"])
        conn = sqlite3.connect(current_app.config['DB_NAME'])
        cur=conn.cursor()
        cur.execute("SELECT titolo_gioco,descrizione_gioco,downloads,nome_file FROM giochi")
        result=cur.fetchall()
        data = []
        for i in result:
            data.append(Gioco(i[0], i[1], i[2], i[3]))
        conn.close()
        if "username" in session:
            return render_template("games.html", data=data, name=session["username"])
        else:
            return render_template("games.html", data=data, name="")

@games.route("/download/<filename>")
def download(filename):
    conn = sqlite3.connect(current_app.config['DB_NAME'])
    cur=conn.cursor()
    cur.execute("UPDATE giochi SET downloads = downloads + 1 WHERE nome_file = ?", (filename, ))
    conn.commit()
    conn.close()
    return send_file(os.path.join(default_path, filename), as_attachment=True)
