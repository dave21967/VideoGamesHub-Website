from flask import Blueprint, render_template, session, redirect, url_for, current_app, request
import sqlite3
import uuid
from smtplib import SMTP
from model import Articolo, Utente, Gioco
import os
from datetime import datetime
#Sezione di gestione dei files
#Posso caricare e cancellare files(immagini) da utilizzare poi all'interno degli articoli
#Un Blueprint è un oggetto che mi permette di descrivere all'interno di files diversi
#Le varie sezioni del sito. Un metodo per mantenere più pulito il codice.
files = Blueprint("files", __name__, template_folder="templates", static_folder="static")

@files.route("/")
def index():
    if "username" in session:
        return render_template("admin/list_files.html", files=os.listdir("static/uploads/images"), name=session["username"])
    else:
        return redirect(url_for('admin.index'))

@files.route("/upload", methods=["GET", "POST"])
def upload():
    immagini = request.files.getlist("images[]")
    for image in immagini:
        image.save(os.path.join("static/uploads/images/",image.filename))
    return redirect(url_for('files.index'))

@files.route("/delete/<filename>")
def delete(filename):
    try:
        os.remove(os.path.join("static/uploads/images", filename))
        return redirect(url_for('files.index'))
    except Exception as e:
        return "Errore: "+str(e)