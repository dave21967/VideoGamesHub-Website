from flask import Flask, render_template, flash, request, redirect, url_for, make_response, session, Blueprint
import sqlite3
from smtplib import SMTP
from datetime import *
from admin import admin
from videogames import games
from model import Articolo

db = "test.db"

user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

@user.route("/<usr>", methods=['GET', 'POST'])
def index(usr):
    if "username" in session:
        conn = sqlite3.connect(current_app.config['DB_NAME'])
        cur=conn.cursor()
        cur.execute("SELECT * FROM articoli ORDER BY data_pubblicazione DESC")
        result = cur.fetchall()
        conn.close()
        if request.args.get("titolo") or request.args.get("filtro"):
            title = request.args.get("titolo")
            filtro = request.args.get("filtro")
            conn = sqlite3.connect(current_app.config['DB_NAME'])
            cur=conn.cursor()
            if filtro == "recente":
                cur.execute("SELECT * FROM articoli WHERE titolo LIKE ? ORDER BY data_pubblicazione DESC", ("%"+title+"%", ))
            elif filtro == "vecchio":
                cur.execute("SELECT * FROM articoli WHERE titolo LIKE ? ORDER BY data_pubblicazione ASC", ("%"+title+"%", ))
            elif filtro == "titolo":
                cur.execute("SELECT * FROM articoli WHERE titolo LIKE ? ORDER BY titolo", ("%"+title+"%", ))
            elif filtro == "views":
                cur.execute("SELECT * FROM articoli WHERE titolo LIKE ? ORDER BY visualizzazioni DESC", ("%"+title+"%", ))
            result = cur.fetchall()
            conn.close()
        return render_template("user.html", data=result, name=usr)
    else:
        return redirect(url_for("articles"))

@user.route("/<usr>/myProfile", methods=["GET", "POST"])
def profile(usr):
    if "username" in session:
        if request.method == "POST":
            uname = request.form['username']
            passwd = request.form['password']
            try:
                conn = sqlite3.connect(current_app.config['DB_NAME'])
                cur=conn.cursor()
                cur.execute("UPDATE utenti SET username = ?, password = PASSWORD(?) WHERE username = ?", (uname, passwd, usr,))
                conn.commit()
                conn.close()
                return redirect(url_for("articles"))
            except Exception as e:
                return "Errore: "+str(e)
        else:
            return render_template("profile.html", username=usr)
    else:
        return redirect(url_for("login"))