from hashlib import md5
#Funzione di cifratura delle password
#utilizza MD5 come algoritmo di hashing
#https://it.wikipedia.org/wiki/MD5
def encrypt_password(pswd):
    return md5(pswd.encode()).hexdigest()
#Questa funzione controlla le password nel momento del login
def check_password(pswd1, pswd2):
    return md5(pswd1.encode()).hexdigest() == pswd2
