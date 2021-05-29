from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, make_response
import sqlite3
import uuid
from smtplib import SMTP
from model import Articolo, Utente, Gioco, Segnalazione, db
import os
from datetime import datetime
from crypt import encrypt_password, check_password
#Sezione di amministrazione del sito
admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

#uso il decoratore @admin per indicare la pagina del sito
@admin.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':#Controllo il metodo di richiesta se è POST
        username = request.form['username'] #significa che l'utente ha effettuato il submit della form di login
        password = request.form['password']
        admins = Utente.query.filter_by(username=username, admin_permissions=1).first()
        if admins and check_password(password, admins.password):
            session["username"] = username
            resp = make_response(redirect(url_for('admin.dashboard')))
            resp.set_cookie("username", username, max_age=60*60*24)
            resp.set_cookie("permissions", "1", max_age=60*60*24)
            return resp
        else:
            return render_template("admin/admin_login.html", error=f"Errore: Nessun utente registrato come {username}")
    else:
        if request.cookies.get("username") and request.cookies.get("permissions") == 'True':
            return redirect(url_for("admin.dashboard"))
        else:
            return render_template("admin/admin_login.html")

#Pagina principale della schermata di amministrazione
#In cui posso visualizzare gli articoli e i giochi pubblicati
@admin.route("/dashboard")
def dashboard():
    if request.cookies.get("username") and request.cookies.get('permissions') == 'True':
        result = Utente.query.filter_by(admin_permissions=0).all()
        arts = Articolo.query.all()
        giochi = Gioco.query.all()
        segn = Segnalazione.query.all()
        return render_template("admin/admin.html", visits=current_app.config['VISITS'], data=result, articles=arts, games=giochi, name=request.cookies.get("username"), segnalazioni=segn)
    else:
        return redirect(url_for("admin.index"))


@admin.route("/add-article", methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        immagine = request.files['images']
        art = Articolo(request.form['titolo'], request.form['contenuto'], request.form['categoria'], str(immagine.filename), request.form['anteprima'])
        try:
            immagine.save(current_app.config['UPLOADS']+immagine.filename)
            db.session.add(art)
            users = Utente.query.filter_by(admin_permissions=0, newsletter=1).all()    
            try:
                if len(users) > 0:
                    m = SMTP("smtp.gmail.com", 587)
                    m.ehlo()
                    m.starttls()
                    m.login("videogameshub01@gmail.com", "Xcloseconnect68")
                    for user in users:
                        m.sendmail("videogameshub01@gmail.com", user.email, "Subject: Nuovo articolo\n\nE' stato pubblicato un nuovo articolo!\nGuardalo subito")
                    m.quit()
            except Exception as e:
                print(e)
            db.session.commit()
            return redirect(url_for('admin.index'))
        except Exception as e:
            return f"Errore: {e}"
    else:
        if request.cookies.get("username"):
            
            return render_template("admin/add_article.html")
        else:
            return redirect(url_for('login'))

@admin.route("/edit-article/<title>", methods=["GET", "POST"])
def edit_article(title):
    if request.cookies.get("username"):
        if request.method == "POST":
            art = Articolo(request.form["titolo"], request.form["contenuto"], request.form["categoria"], "", request.form["anteprima"])
            art = Articolo.query.filter_by(titolo=title).first()
            art.titolo = request.form["titolo"]
            art.contenuto = request.form["contenuto"]
            art.categoria = request.form["categoria"]
            art.anteprima = request.form["anteprima"]
            db.session.commit()
            return redirect(url_for("admin.dashboard"))
        else:
            art=Articolo.query.filter_by(titolo=title).first()
            return render_template("admin/edit_article.html", title=art.titolo, content=art.contenuto, preview=art.anteprima, cathegory=art.categoria)
    else:
        return redirect(url_for("admin.index"))

@admin.route("/edit-game/<title>", methods=["GET", "POST"])
def edit_game(title):
    if request.cookies.get("username"):
        if request.method == "POST":
            gioco = Gioco(request.form["titolo"], request.form["descrizione"], "", "")
            game = Gioco.query.filter_by(titolo_gioco=title).first()
            game.titolo = request.form["titolo"]
            game.descrizione = request.form["descrizione"]
            db.session.commit()
            return redirect(url_for("admin.dashboard"))
        else:
            gioco = Gioco.query.filter_by(titolo=title).first()#Un esempio di query fatta con SQLAlchemy
            return render_template("admin/edit_game.html", game=gioco)#Libreria ORM compatibile con Flask
    else:#https://flask-sqlalchemy.palletsprojects.com/en/2.x/
        return redirect(url_for("admin.index"))

@admin.route("/delete-article/<title>")
def delete_article(title):
    if "username" in session:
        art = Articolo.query.filter_by(titolo=title).first()
        Articolo.query.filter(Articolo.titolo==title).delete()
        os.remove(os.path.join(current_app.config["UPLOADS"], art.immagini))
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("login"))

@admin.route("/add-game", methods=["GET", "POST"])
def add_game():
    if request.cookies.get("username"):
        if request.method == "POST":
            title = request.form["titolo"]
            descr = request.form["descrizione"]
            game = request.files["gioco"]
            try:
                g = Gioco(title, descr, 0, game.filename)
                game.save(os.path.join(current_app.config["GAMES-UPLOADS"], game.filename))
                db.session.add(g)
                db.session.commit()
                return redirect(url_for("admin.dashboard"))
            except Exception as e:
                return f"Errore: {e}"
        else:
            return render_template("admin/add_game.html")
    else:
        return redirect(url_for("login"))

@admin.route("/delete-game/<title>")
def delete_game(title):
    if request.cookies.get("username"):
        g=Gioco.query.filter_by(titolo=title).first()
        Gioco.query.filter(Gioco.titolo==title).delete()
        os.remove(os.path.join(current_app.config["GAMES-UPLOADS"], g.nome_file))
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("login"))

@admin.route("/add-admin-user", methods=["GET", "POST"])
def add_admin():
    if request.cookies.get("username"):
        if request.method == "POST":
            try:
                username = request.form["username"]
                email = request.form["email"]
                password = request.form["password"]
                usr = Utente(username, email, encrypt_password(password), 1)
                db.session.add(usr)
                db.session.commit()
                return redirect(url_for("admin.dashboard"))
            except Exception as e:
                return render_template("admin/add_admin.html", error=f"Errore nel salvataggio: {str(e)}")
        else:
            return  render_template("admin/add_admin.html", name=request.cookies.get("username"))
    else:
        return redirect(url_for('admin.login'))