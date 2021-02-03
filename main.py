from flask import Flask, render_template, flash, request, redirect, url_for, make_response, session
import mysql.connector as mysql
from smtplib import SMTP
from threading import Thread
from datetime import *
from admin import admin

mysql_user = "root"
mysql_password = None

class Articolo(object):
    def __init__(self, titolo, contenuto, categoria, immagine):
        self.titolo = titolo
        self.contenuto = contenuto
        self.categoria = categoria
        self.immagine = immagine

app = Flask(__name__)
app.secret_key = 'hello world!'
app.config['UPLOADS'] = './static/uploads/'
app.config['VISITS'] = 0
app.config['HOSTS'] = []

app.register_blueprint(admin, url_prefix="/admin")

@app.route("/")
def index():
    if request.host not in app.config['HOSTS']:
        app.config['HOSTS'].append(request.host)
        app.config['VISITS'] += 1
    return render_template("index.html")

@app.route("/contacts")
def contacts():
    return render_template('contacts.html')

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
        cur = conn.cursor()
        cur.execute("SELECT username, password FROM utenti WHERE username = %s AND password = PASSWORD(%s)", (username, password))
        if len(cur.fetchall()) > 0:
            conn.close()
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('user', usr=username))
        else:
            return f"<h1>Errore: Nessun utente registrato come {username}</h1>"
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
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
            conn = mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO utenti VALUES ('0',%s,%s,PASSWORD(%s),1)", (username, email, password))
                conn.commit()
                conn.close()
                mail = SMTP("smtp.gmail.com", 587)
                mail.ehlo()
                mail.starttls()
                mail.login("videogameshub01@gmail.com", "Xcloseconnect68")
                mail.sendmail("videogameshub01@gmail.com", "davide.costantini2001@gmail.com", "Subject: Nuova iscrizione\n\nUn nuovo utente e' entrato nella community!\n"+username+"")
                mail.sendmail("videogameshub01@gmail.com", email, "Subject: Benvenuto"+username+"!\n\nBenvenuto nella nostra community!!!")
                mail.quit()
                session['username'] = username
                return redirect(url_for('user', usr=username))
            except Exception as e:
                return render_template("signup.html", error=f"Errore: {e}")
    else:
        return render_template("signup.html", error="")

@app.route("/articles/<usr>", methods=['GET', 'POST'])
def user(usr):
    if request.method == "POST":
        article_id = request.form['article_id']
        text = request.form['commentText']
        conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
        cur=conn.cursor()
        cur.execute("SELECT id FROM utenti WHERE username = %s", (usr,))
        result = cur.fetchall()
        user_id = result[0][0]
        cur.execute("INSERT INTO commenti VALUES (0,%s,%s,%s)", (article_id, user_id, text))
        conn.commit()
        conn.close()
        return redirect(url_for('user', usr=session['username']))
    else:
        if "username" in session:
            conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
            cur=conn.cursor()
            cur.execute("SELECT * FROM articoli ORDER BY visualizzazioni")
            result = cur.fetchall()
            conn.close()
            if request.args.get("titolo"):
                title = request.args.get("titolo")
                conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
                cur=conn.cursor()
                cur.execute("SELECT * FROM articoli WHERE titolo = %s ORDER BY visualizzazioni", (title, ))
                result = cur.fetchall()
                conn.close()
            return render_template("user.html", data=result, name=usr)
        else:
            return redirect(url_for("articles"))

@app.route("/articles", methods=["GET", "POST"])
def articles():
    if request.args.get("titolo"):
        title = request.args.get("titolo")
        conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
        cur=conn.cursor()
        cur.execute("SELECT * FROM articoli WHERE titolo = %s ORDER BY visualizzazioni", (title, ))
        result = cur.fetchall()
        conn.close()
    else:
        conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
        cur=conn.cursor()
        cur.execute("SELECT * FROM articoli ORDER BY visualizzazioni")
        result = cur.fetchall()
        conn.close()
    return render_template("user.html", data=result, name="")

@app.route("/articles/view/<title>")
def view_article(title):
    conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
    cur=conn.cursor()
    cur.execute("SELECT * FROM articoli WHERE titolo = %s", (title,))
    result = cur.fetchall()
    cur.execute("UPDATE articoli SET visualizzazioni = visualizzazioni + 1 WHERE titolo = %s", (title, ))
    conn.commit()
    conn.close()
    return render_template("article.html", title=title, content=f"{result[0][2]}")

@app.route("/<usr>/myProfile", methods=["GET", "POST"])
def profile(usr):
    if "username" in session:
        if request.method == "POST":
            uname = request.form['username']
            passwd = request.form['password']
            try:
                conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
                cur=conn.cursor()
                cur.execute("UPDATE utenti SET username = %s, password = PASSWORD(%s) WHERE username = %s", (uname, passwd, usr,))
                conn.commit()
                conn.close()
                return redirect(url_for("articles"))
            except Exception as e:
                return "Errore: "+str(e)
        else:
            return render_template("profile.html", username=usr)
    else:
        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")