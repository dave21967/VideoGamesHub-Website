from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from smtplib import SMTP
from datetime import *
from admin import admin
from videogames import games
from user import user
from model import Articolo
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'hello world!'
app.config['UPLOADS'] = 'static/uploads/'
app.config['GAMES-UPLOADS'] = "static/uploads/games/"
app.config['DB_NAME'] = "videogameshub.db"
app.config['VISITS'] = 0
app.config['HOSTS'] = []

app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(games, url_prefix="/games")
app.register_blueprint(user, url_prefix="/user")

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
        conn = sqlite3.connect(app.config['DB_NAME'])
        cur = conn.cursor()
        cur.execute("SELECT username, password FROM utenti WHERE username = ? AND password = ?", (username, password))
        if len(cur.fetchall()) > 0:
            conn.close()
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
            conn = sqlite3.connect(app.config['DB_NAME'])
            cur = conn.cursor()
            try:
                cur.execute(f"INSERT INTO utenti VALUES (?,?,?,1,1)", (username, email, password,))
                conn.commit()
                conn.close()
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
        conn = sqlite3.connect(app.config['DB_NAME'])
        cur=conn.cursor()
        cur.execute("SELECT * FROM articoli WHERE titolo LIKE ?", ("%"+title+"%", ))
        result = cur.fetchall()
        conn.close()
    else:
        conn = sqlite3.connect(app.config['DB_NAME'])
        cur=conn.cursor()
        cur.execute("SELECT * FROM articoli ORDER BY data_pubblicazione DESC")
        result = cur.fetchall()
        conn.close()
    if "username" in session:
        return render_template("user.html", data=result, name=session["username"])
    else:
        return render_template("user.html", data=result, name="")

@app.route("/articles/view/<title>")
def view_article(title):
    conn = sqlite3.connect(app.config['DB_NAME'])
    cur=conn.cursor()
    cur.execute("SELECT * FROM articoli WHERE titolo = ?", (title,))
    result = cur.fetchall()
    cur.execute("UPDATE articoli SET visualizzazioni = visualizzazioni + 1 WHERE titolo = ?", (title, ))
    for i in result:
        art = Articolo(i[0],i[1],[3],i[2],i[6])
    conn.commit()
    conn.close()
    if "username" in session:
        return render_template("article.html", title=title, content=f"{art.contenuto}", name=session["username"])
    else:
        return render_template("article.html", title=title, content=f"{art.contenuto}")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
