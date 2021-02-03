from flask import Blueprint, render_template, session, redirect, url_for, current_app, request
import mysql.connector as mysql

mysql_user = "root"
mysql_password = None

admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

@admin.route("/")
def index():
    if 'username' in session:
        conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
        cur=conn.cursor()
        cur.execute("SELECT * FROM utenti WHERE username <> 'admin'")
        result = cur.fetchall()
        cur.execute("SELECT titolo,categoria,data_pubblicazione FROM articoli")
        arts = cur.fetchall()
        conn.close()
        return render_template("admin.html", visits=current_app.config['VISITS'], data=result, articles=arts)
    else:
        return redirect(url_for("login"))

@admin.route("/add-article", methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        art = Articolo(request.form['titolo'], request.form['contenuto'], request.form['categoria'], request.files['images'])
        try:
            art.immagine.save(app.config['UPLOADS']+art.immagine.filename)
            conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
            cur=conn.cursor()
            cur.execute("INSERT INTO articoli VALUES ('0',%s,%s,%s,%s, NOW())", (art.titolo, art.contenuto, art.immagine.filename, art.categoria))
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
            conn=mysql.connect(host="localhost", user=mysql_user, password=mysql_password, database="VideoGamesHub")
            cur=conn.cursor()
            cur.execute("SELECT nome FROM categorie")
            ris = cur.fetchall()
            data = []
            for i in ris:
                data.append(i[0])
            conn.close()
            return render_template("add_article.html", data=data)
        else:
            return redirect(url_for('login'))
