from flask import Flask, render_template, flash, request, redirect, url_for, make_response, session, Blueprint
import sqlite3
from smtplib import SMTP
from datetime import *
from admin import admin
from videogames import games
from slugify import slugify
from model import Articolo, PostSalvato, db

user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

@user.route("/<usr>/myProfile", methods=["GET", "POST"])
def profile(usr):
    if "username" in session:
        posts = PostSalvato.query.filter_by(utente=usr).all()
        print(posts)
        return render_template("profile.html", posts=posts, username=usr, name=session["username"])
    else:
        return redirect(url_for("login"))

@user.route("<usr>/save-post/<post>")
def save_post(usr, post):
    if "username" in session:
        post_to_save = PostSalvato(utente=usr, articolo=post)
        db.session.add(post_to_save)
        db.session.commit()
        return "Post salvato!"
    else:
        return redirect(url_for('login'))