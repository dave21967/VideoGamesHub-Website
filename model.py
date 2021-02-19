class Articolo(object):
    def __init__(self, titolo, contenuto, categoria, immagine, anteprima):
        self.titolo = titolo
        self.contenuto = contenuto
        self.categoria = categoria
        self.immagine = immagine
        self.anteprima = anteprima

class Gioco(object):
    def __init__(self, titolo, descrizione, downloads, filename):
        self.titolo = titolo
        self.descrizione = descrizione
        self.downloads = downloads
        self.nome_file = filename

class Utente(object):
    def __init__(self, username, email, password, newsletter, admin_permissions):
        self.username = username
        self.password = password
        self.email = email
        self.newsletter = newsletter
        self.admin_permissions = admin_permissions