from django.db import connection
from hashlib import sha256

def create_account(email, username, password, pin):
    response = {"message":"Buat akun berhasil","valid":True}
    try:
        with connection.cursor() as cursor:

            sql = "select id from users where email=%s"
            cursor.execute(sql,[email])
            if (cursor.fetchone()):
                response["message"]="Login gagal karena email sudah terpakai"
                response["valid"]=False
                return response
            if (len(password) < 8):
                response["message"]="Password terlalu pendek minimal 8 digit ya"
                response["valid"]=False

            sql = """
                INSERT INTO users (username, email, password, pin, photo_profile)
                VALUES (%s, %s, %s, %s, %s)
            """
            password = sha256(password.encode('utf-8')).hexdigest()
            values = [username, email, password, str(pin), "photo_profile/default.jpg"]
            cursor.execute(sql, values)

    except Exception as e:
        print("ERROR:", e)
    return response

def login_user(email,password):
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT id FROM users WHERE email=%s AND password=%s
            """
            password = sha256(password.encode('utf-8')).hexdigest()

            values = [email,password]
            cursor.execute(sql,values)
            if (len(cursor.fetchone())>0):
                return True
            else:
                return False
            
    except Exception as e:
        print(e)
