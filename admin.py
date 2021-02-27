from flask import Blueprint, render_template, session, redirect, url_for, current_app, request
import sqlite3
import uuid
from smtplib import SMTP
from model import Articolo, Utente, Gioco
import os
from datetime import datetime

admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

@admin.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(current_app.config['DB_NAME'])
        cur = conn.cursor()
        cur.execute("SELECT username, password FROM utenti WHERE username = ? AND password = ? AND permessi_admin = 1", (username, password))
        if len(cur.fetchall()) > 0:
            conn.close()
            session['username'] = username
            session['permissions'] = 1
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template("admin_login.html", error=f"Errore: Nessun utente registrato come {username}")
    else:
        if "username" in session and session["permissions"] == 1:
            return redirect(url_for("admin.dashboard"))
        else:
            return render_template("admin_login.html")


@admin.route("/dashboard")
def dashboard():
    if 'username' in session:
        conn = sqlite3.connect(current_app.config['DB_NAME'])
        cur=conn.cursor()
        cur.execute("SELECT * FROM utenti WHERE username <> 'admin'")
        result = cur.fetchall()
        cur.execute("SELECT titolo,categoria,data_pubblicazione FROM articoli")
        arts = cur.fetchall()
        cur.execute("SELECT titolo_gioco,descrizione_gioco,downloads FROM giochi")
        giochi = cur.fetchall()
        conn.close()
        return render_template("admin.html", visits=current_app.config['VISITS'], data=result, articles=arts, games=giochi, name=session["username"])
    else:
        return redirect(url_for("admin.index"))


@admin.route("/add-article", methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        art = Articolo(request.form['titolo'], request.form['contenuto'], request.form['categoria'], request.files['images'], request.form['anteprima'])
        try:
            art.immagine.save(current_app.config['UPLOADS']+art.immagine.filename)
            conn = sqlite3.connect(current_app.config['DB_NAME'])
            cur=conn.cursor()
            cur.execute("INSERT INTO articoli VALUES (?,?,?,?,?,?,?)", (art.titolo, art.contenuto, art.immagine.filename, art.categoria,datetime.today().strftime("%d-%m-%Y"), 0,art.anteprima))
            cur.execute("SELECT email FROM utenti WHERE username <> 'admin' AND newsletter = 1")
            emails = cur.fetchall()
            if len(emails) > 0:
                m = SMTP("smtp.gmail.com", 587)
                m.ehlo()
                m.starttls()
                m.login("videogameshub01@gmail.com", "Xcloseconnect68")
                for mail in emails[0]:
                    m.sendmail("videogameshub01@gmail.com", mail, "Subject: Nuovo articolo\n\nE' stato pubblicato un nuovo articolo!\nGuardalo subito")
                m.quit()
            conn.commit()
            conn.close()
            return redirect(url_for('admin.index'))
        except Exception as e:
            return f"Errore: {e}"
    else:
        if "username" in session:
            
            return render_template("add_article.html")
        else:
            return redirect(url_for('login'))

@admin.route("/edit-article/<title>", methods=["GET", "POST"])
def edit_article(title):
    if "username" in session:
        if request.method == "POST":
            art = Articolo(request.form["titolo"], request.form["contenuto"], request.form["categoria"], "", request.form["anteprima"])
            conn = sqlite3.connect(current_app.config["DB_NAME"])
            cur = conn.cursor()
            cur.execute("UPDATE articoli SET titolo = ?, contenuto = ?, categoria = ?, anteprima_testo = ? WHERE titolo = ?", (art.titolo, art.contenuto, art.categoria, art.anteprima, title,))
            conn.commit()
            conn.close()
            return redirect(url_for("admin.dashboard"))
        else:
            conn = sqlite3.connect(current_app.config["DB_NAME"])
            cur = conn.cursor()
            cur.execute("SELECT titolo, contenuto, categoria, anteprima_testo FROM articoli WHERE titolo = ?", (title, ))
            result = cur.fetchall()
            for i in result:
                art = Articolo(i[0], i[1], i[2], "", i[3])
            conn.commit()
            conn.close()
            return render_template("edit_article.html", title=art.titolo, content=art.contenuto, preview=art.anteprima, cathegory=art.categoria)
    else:
        return redirect(url_for("admin.index"))

@admin.route("/edit-game/<title>", methods=["GET", "POST"])
def edit_game(title):
    if "username" in session:
        if request.method == "POST":
            gioco = Gioco(request.form["titolo"], request.form["descrizione"], "", "")
            conn = sqlite3.connect(current_app.config["DB_NAME"])
            cur = conn.cursor()
            cur.execute("UPDATE giochi SET titolo_gioco = ?, descrizione_gioco = ? WHERE titolo_gioco = ?", (gioco.titolo,gioco.descrizione, title,))
            conn.commit()
            conn.close()
            return redirect(url_for("admin.dashboard"))
        else:
            conn = sqlite3.connect(current_app.config["DB_NAME"])
            cur = conn.cursor()
            cur.execute("SELECT titolo_gioco, descrizione_gioco FROM giochi WHERE titolo_gioco = ?", (title, ))
            result = cur.fetchall()
            for i in result:
                gioco = Gioco(i[0], i[1],"","")
            conn.commit()
            conn.close()
            return render_template("edit_game.html", game=gioco)
    else:
        return redirect(url_for("admin.index"))

@admin.route("/delete-article/<title>")
def delete_article(title):
    if "username" in session:
        conn = sqlite3.connect(current_app.config["DB_NAME"])
        cur=conn.cursor()
        cur.execute("SELECT immagini FROM articoli WHERE titolo = ?", (title, ))
        result=cur.fetchall()
        cur.execute("DELETE FROM articoli WHERE titolo = ?", (title, ))
        os.remove(os.path.join(current_app.config["UPLOADS"], str(result[0][0])))
        conn.commit()
        conn.close()
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("login"))

@admin.route("/add-game", methods=["GET", "POST"])
def add_game():
    if "username" in session:
        if request.method == "POST":
            title = request.form["titolo"]
            descr = request.form["descrizione"]
            game = request.files["gioco"]
            try:
                conn = sqlite3.connect(current_app.config['DB_NAME'])
                cur=conn.cursor()
                cur.execute("INSERT INTO giochi VALUES (?,?,?,0,?)", (title, datetime.today().strftime("%d-%m-%Y"),game.filename, descr))
                conn.commit()
                conn.close()
                game.save(os.path.join(current_app.config["GAMES-UPLOADS"], game.filename))
                return redirect(url_for("admin.dashboard"))
            except Exception as e:
                return f"Errore: {e}"
        else:
            return render_template("add_game.html")
    else:
        return redirect(url_for("login"))

@admin.route("/delete-game/<title>")
def delete_game(title):
    if "username" in session:
        conn = sqlite3.connect(current_app.config["DB_NAME"])
        cur=conn.cursor()
        cur.execute("SELECT nome_file FROM giochi WHERE titolo_gioco = ?", (title, ))
        result=cur.fetchall()
        cur.execute("DELETE FROM giochi WHERE titolo_gioco = ?", (title, ))
        os.remove(os.path.join(current_app.config["GAMES-UPLOADS"], str(result[0][0])))
        conn.commit()
        conn.close()
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("login"))

@admin.route("/add-admin-user", methods=["GET", "POST"])
def add_admin():
    if "username" in session:
        if request.method == "POST":
            try:
                username = request.form["username"]
                email = request.form["email"]
                password = request.form["password"]
                usr = Utente(username,email,password,1,1)
                conn = sqlite3.connect(current_app.config["DB_NAME"])
                cur = conn.cursor()
                cur.execute("INSERT INTO utenti VALUES (?,?,?,1,1)",(usr.username,usr.email,usr.password,))
                conn.commit()
                conn.close()
                return redirect(url_for("admin.dashboard"))
            except Exception as e:
                return render_template("add_admin.html", error=f"Errore nel salvataggio: {str(e)}")
        else:
            return  render_template("add_admin.html", name=session["username"])
    else:
        return redirect(url_for('admin.login'))