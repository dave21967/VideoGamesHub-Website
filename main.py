from flask import Flask, render_template, flash, request, redirect, url_for, make_response, session
import mysql.connector as mysql
import base64

class Articolo(object):
    def __init__(self, titolo, contenuto, categoria, immagine):
        self.titolo = titolo
        self.contenuto = contenuto
        self.categoria = categoria
        self.immagine = immagine

app = Flask(__name__)
app.secret_key = 'hello world!'
app.config['UPLOADS'] = './static/uploads/'

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connect(host="localhost", user="root", password="root", database="VideoGamesHub")
        cur = conn.cursor()
        cur.execute("SELECT username, password FROM utenti WHERE username = %s AND password = PASSWORD(%s)", (username, password))
        if len(cur.fetchall()) > 0:
            conn.close()
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin'))
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
        conn = mysql.connect(host="localhost", user="root", password="root", database="VideoGamesHub")
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO utenti VALUES ('0',%s,%s,PASSWORD(%s))", (username, email, password))
            conn.commit()
            conn.close()
            session['username'] = username
            return redirect(url_for('user', usr=username))
        except Exception as e:
            return f"Errore: {e}"
    else:
        return render_template("signup.html")

@app.route("/<usr>")
def user(usr):
    if "username" in session:
        conn=mysql.connect(host="localhost", user="root", password="root", database="VideoGamesHub")
        cur=conn.cursor()
        cur.execute("SELECT * FROM articoli")
        result = cur.fetchall()
        conn.close()
        return render_template("user.html", data=result, name=usr)
    else:
        return redirect(url_for("login"))


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        art = Articolo(request.form['titolo'], request.form['contenuto'], request.form['categoria'], request.files['images'])
        try:
            art.immagine.save(app.config['UPLOADS']+art.immagine.filename)
            conn=mysql.connect(host="localhost", user="root", password="root", database="VideoGamesHub")
            cur=conn.cursor()
            cur.execute("INSERT INTO articoli VALUES ('0',%s,%s,%s,%s)", (art.titolo, art.contenuto, art.immagine.filename, art.categoria))
            conn.commit()
            conn.close()
            return redirect(url_for('admin'))
        except Exception as e:
            return f"Errore: {e}"
    else:
        if "username" in session:
            conn=mysql.connect(host="localhost", user="root", password="root", database="VideoGamesHub")
            cur=conn.cursor()
            cur.execute("SELECT nome FROM categorie")
            ris = cur.fetchall()
            data = []
            for i in ris:
                data.append(i[0])
            conn.close()
            return render_template("admin.html", data=data)
        else:
            return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", ssl_context=("cert.pem", "key.pem"))