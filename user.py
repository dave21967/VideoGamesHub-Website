from flask import Flask, render_template, flash, request, redirect, url_for, make_response, session, Blueprint
import sqlite3
from smtplib import SMTP
from datetime import *
from admin import admin
from videogames import games
from model import Articolo

user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

@user.route("/<usr>/myProfile", methods=["GET", "POST"])
def profile(usr):
    if "username" in session:
        return render_template("profile.html", username=usr, name=session["username"])
    else:
        return redirect(url_for("login"))