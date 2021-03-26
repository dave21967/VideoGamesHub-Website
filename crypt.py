from hashlib import md5

def encrypt_password(pswd):
    return md5(pswd.encode()).hexdigest()

def check_password(pswd1, pswd2):
    return md5(pswd1.encode()).hexdigest() == pswd2
