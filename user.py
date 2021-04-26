from flask import Flask, render_template, flash, request, redirect, url_for, make_response, session, Blueprint
import sqlite3
from smtplib import SMTP
from datetime import *
from admin import admin
from videogames import games
from model import Articolo, PostSalvato, Gioco, Punteggio, db

user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

@user.route("/<usr>/myProfile", methods=["GET", "POST"])
def profile(usr):
    if "username" in session:
        posts = PostSalvato.query.filter_by(utente=usr).all()
        games = Gioco.query.all()
        return render_template("profile.html", posts=posts, games=games, username=usr, name=session["username"])
    else:
        return redirect(url_for("login"))

@user.route("/<usr>/scoreboard")
def scoreboard(usr):
    if "username" in session:
        scores = Punteggio.query.all()
        return render_template("scoreboard.html", scores=scores)
    else:
        return redirect(url_for('login'))

@user.route("<usr>/save-post/<post>")
def save_post(usr, post):
    if "username" in session:
        post_to_save = PostSalvato(utente=usr, articolo=post)
        db.session.add(post_to_save)
        db.session.commit()
        return redirect("/articles/view/"+post)
    else:
        return redirect(url_for('login'))

@user.route("<usr>/save-score/")
def save_score(usr):
    if request.args:
        scores = Punteggio.query.filter_by(nome_utente=usr, titolo_gioco=request.args["titolo_gioco"]).first()
        if scores:
            return "Il punteggio esiste già nel database!"
        else:
            score = Punteggio(nome_utente=usr, titolo_gioco=request.args["titolo_gioco"], punteggio=request.args["score"])
            db.session.add(score)
            db.session.commit()
            return redirect(url_for('user.profile', usr=usr))

@user.route("<usr>/unsave-post/<title>")
def unsave_post(usr, title):
    post = PostSalvato.query.filter_by(articolo=title).first()
    if post:
        PostSalvato.query.filter_by(articolo=title).delete()
        db.session.commit()
    
    return redirect("/articles/view/"+title)

@user.route("<usr>/delete-score/")
def delete_score(usr):
    score=Punteggio.query.filter_by(nome_utente=usr).first()
    if score:
        Punteggio.query.filter_by(nome_utente=usr).delete()
        db.session.commit()
        return redirect(url_for('user.profile', usr=usr))

@user.route("set-theme/")
def set_theme():
    if 'theme' in request.args:
        resp = make_response()
        resp.set_cookie("theme", request.args['theme'], max_age=60*60*24)
        return resp

@user.route("get_cookie/<cookie>")
def get_cookie(cookie):
    if cookie in request.cookies:
        return request.cookies[cookie]
    else:
        return "Nessun cookie "+cookie