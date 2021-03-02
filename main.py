from flask import render_template, request, redirect, url_for, session
from smtplib import SMTP
import sqlite3
from datetime import *
from admin import admin
from videogames import games
from files import files
from user import user
from model import Utente, db, app, Articolo
import os

app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(games, url_prefix="/games")
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(files, url_prefix="/files")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.host not in app.config['HOSTS']:
        app.config['HOSTS'].append(request.host)
        app.config['VISITS'] += 1
    if request.method == "POST":
        question = request.form.get("question")
        mail = SMTP("smtp.gmail.com", 587)
        mail.ehlo()
        mail.starttls()
        mail.login("videogameshub01@gmail.com", "Xcloseconnect68")
        mail.sendmail("videogameshub01@gmail.com", "davide.costantini2001@gmail.com", "Subject: Nuova domanda\n\nUn utente ha posto la seguente domanda\n"+question+"")
        mail.quit()
        return render_template("index.html")
    else:
        if "username" in session:
            return render_template("index.html", name=session["username"])
        else:
            return render_template("index.html")

@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        if request.method == "POST":
            problem = request.form.get("problem")
            mail = SMTP("smtp.gmail.com", 587)
            mail.ehlo()
            mail.starttls()
            mail.login("videogameshub01@gmail.com", "Xcloseconnect68")
            mail.sendmail("videogameshub01@gmail.com", "davide.costantini2001@gmail.com", "Subject: E' stato segnalato un problema\n\nUn utente ha segnalato un problema\n"+problem+"")
            mail.quit()
            return render_template("contacts.html", name=session["username"])
    else:
        if "username" in session:
            return render_template("contacts.html", name=session["username"])
        else:
            return render_template("contacts.html")

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = Utente.query.filter_by(username=username, password=password).all()
        if len(users) > 0:
            session['username'] = username
            session['permissions'] = 0
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error=f"Nessun utente trovato con il nome di{username}")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("permissions", None)
    return redirect(url_for('index'))

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        if not email or not password or not username:
            return render_template("signup.html", error="Tutti i campi sono obbligatori")
        else:
            try:
                usr = Utente(username, email, password, 0)
                db.session.add(usr)
                db.session.commit()
                mail = SMTP("smtp.gmail.com", 587)
                mail.ehlo()
                mail.starttls()
                mail.login("videogameshub01@gmail.com", "Xcloseconnect68")
                mail.sendmail("videogameshub01@gmail.com", "davide.costantini2001@gmail.com", "Subject: Nuova iscrizione\n\nUn nuovo utente e' entrato nella community!\n"+username+"")
                mail.sendmail("videogameshub01@gmail.com", email, "Subject: Benvenuto "+username+"!\n\nBenvenuto nella nostra community!!!")
                mail.quit()
                session['username'] = username
                return redirect(url_for('index'))
            except Exception as e:
                return render_template("signup.html", error=f"Errore: {e}")
    else:
        return render_template("signup.html", error="")

@app.route("/articles", methods=["GET", "POST"])
def articles():
    if request.args.get("titolo"):
        title = request.args.get("titolo")
        result=Articolo.query.filter(Articolo.titolo.like(f"%{title}%"))
    else:
        result = Articolo.query.order_by(Articolo.data_pubblicazione.desc())
    if "username" in session:
        return render_template("user.html", data=result, name=session["username"])
    else:
        return render_template("user.html", data=result, name="")

@app.route("/articles/view/<title>")
def view_article(title):
    arts = Articolo.query.filter_by(titolo=title)
    if "username" in session:
        return render_template("article.html", article=arts, name=session["username"])
    else:
        return render_template("article.html", article=arts)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host="0.0.0.0")
