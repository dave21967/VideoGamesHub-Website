from flask import render_template, request, redirect, url_for, session, send_file, make_response
from smtplib import SMTP
import sqlite3
from datetime import *
from admin import admin
from videogames import games
from files import files
from user import user
from model import Utente, db, app, Articolo, Commento, PostSalvato
from crypt import encrypt_password, check_password
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
        if request.cookies.get("username"):
            return render_template("index.html", name=request.cookies.get("username"))
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
            return render_template("contacts.html", name=request.cookies.get("username"))
    else:
        if "username" in session:
            return render_template("contacts.html", name=request.cookies.get("username"))
        else:
            return render_template("contacts.html")

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = Utente.query.filter_by(username=username).first()
        if users and check_password(password, users.password):
            session["username"] = username
            resp=make_response(redirect(url_for('index')))
            resp.set_cookie("username", username, max_age=60*60*24)
            resp.set_cookie("permissions", "0", max_age=60*60*24)
            return resp
        else:
            return render_template("login.html", error=f"Nessun utente trovato con il nome di{username}")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("permissions", None)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie("username", "", expires=0)
    resp.set_cookie("permissions", "", expires=0)
    return resp

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
                usr = Utente(username, email, encrypt_password(password), 0)
                db.session.add(usr)
                db.session.commit()
                mail = SMTP("smtp.gmail.com", 587)
                mail.ehlo()
                mail.starttls()
                mail.login("videogameshub01@gmail.com", "Xcloseconnect68")
                mail.sendmail("videogameshub01@gmail.com", "davide.costantini2001@gmail.com", "Subject: Nuova iscrizione\n\nUn nuovo utente e' entrato nella community!\n"+username+"")
                mail.sendmail("videogameshub01@gmail.com", email, "Subject: Benvenuto "+username+"!\n\nBenvenuto nella nostra community!!!")
                mail.quit()
                return redirect(url_for('login'))
            except Exception as e:
                return render_template("signup.html", error=f"Errore: {e}")
    else:
        return render_template("signup.html", error="")

@app.route("/check-users")
def check_users():
    username=request.args["username"]
    email=request.args["email"]
    password=request.args["password"]
    usr=Utente.query.filter_by(username=username, email=email).first()
    if usr is not None:
        print("Già esistente!")
        resp = make_response("Già esistente")
        return resp
    else:
        resp = make_response("Ok")
        print(resp)
        return resp

@app.route("/articles/<page>", methods=["GET", "POST"])
def articles(page):
    if request.args.get("titolo"):
        title = request.args.get("titolo")
        result=Articolo.query.filter(Articolo.titolo.like(f"%{title}%")).paginate(int(page), per_page=5)
    else:
        result = Articolo.query.order_by(Articolo.data_pubblicazione.desc()).paginate(int(page), per_page=5)
    if request.cookies.get("username"):
        return render_template("blog-feed.html", data=result, name=request.cookies.get("username"))
    else:
        return render_template("blog-feed.html", data=result, name="")

@app.route("/articles")
def search_article():
    titolo = request.args["titolo"]
    result = Articolo.query.filter(Articolo.titolo.like(f"%{titolo}%")).first()
    if result:
        return make_response(result.slug)

@app.route("/articles/view/<title>", methods=["GET", "POST"])
def view_article(title):
    if request.method == "POST":
        utente = request.form["user"]
        testo = request.form["testo"]
        articolo = request.form["articolo"]
        try:
            comment = Commento(testo, utente, articolo)
            db.session.add(comment)
            db.session.commit()
            return redirect(request.url)
        except Exception as e:
            return str(e)
    else:
        arts = Articolo.query.filter_by(slug=title).first()
        arts.visualizzazioni += 1
        comments = Commento.query.filter_by(titolo_articolo=arts.titolo).all()
        db.session.commit()
        if request.cookies.get("username"):
            saved = "false"
            art = PostSalvato.query.filter_by(articolo=title, utente=session['username']).first()
            if art != None:
                saved = "true"
            else:
                saved = "false"
            return render_template("article.html", article=arts, saved=saved, name=request.cookies.get("username"), commenti=comments)
        else:
            return render_template("article.html", article=arts, commenti=comments)

@app.route("/download-app")
def download_app():
    return render_template("download_app.html")

@app.route("/download-app/download")
def download():
    return send_file("static/uploads/sfondo1.jpg", as_attachment=True)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host="0.0.0.0")
