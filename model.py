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