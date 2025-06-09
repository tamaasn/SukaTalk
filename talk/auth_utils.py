from django.db import connection
from hashlib import sha256
import random
from datetime import datetime
from zoneinfo import ZoneInfo

chars = "qwertyuiopasdfghjklzxcvbnm1234567890"
char_length=len(chars)
tz = ZoneInfo("Asia/Jakarta")
now_utc = datetime.now(tz)

def get_member_channels(channel):
    sql = "select user_id from channels where id=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql,[channel])
        members = []
        for i in cursor.fetchall():
            members.append(i[0])
        return members

def database_update_profile(username, avatar_file, id_):
    sql = "update users set username=%s, photo_profile=%s where id=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql,[username,avatar_file,id_])

def get_friend_info(user_id,channel):
    sql = "select friend from friends where user=%s and channel_id=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql,[user_id,channel])
        member = cursor.fetchall()[0][0]
        return member

def get_member_event(members):
    sql = "select event from events where user_id=%s"
    results=[]
    with connection.cursor() as cursor:
        for i in members:
            cursor.execute(sql,[i])
            results.append(cursor.fetchall()[0][0])
        return results
            

def insert_message(channel,user_id,message):
    sekarang=datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    print("Sekarang:",sekarang)
    sql = "insert into messages (channel,user_id,message,timestamp) values (%s,%s,%s,%s)"
    with connection.cursor() as cursor:
        cursor.execute(sql,[channel,user_id,message,sekarang])
        sql = "select user_id from channels where id=%s"
        cursor.execute(sql,[channel])
        data = cursor.fetchall()
        for i in data:
            sql = "update friends set last_timestamp=%s, last_message=%s, seen={} where user=%s and channel_id=%s".format(i[0] is user_id)
            cursor.execute(sql,[sekarang,message,i[0],channel])

def set_seen_message(channel,user_id):
    with connection.cursor() as cursor:
        sql = "update friends set seen=1 where user=%s and channel_id=%s"
        cursor.execute(sql,[user_id,channel])

def randomize():
    result=""
    for i in range(6):
        result += str(random.randint(0,9))
    return result 

def randomize_channel():
    result = ""
    for i in range(15):
        result += chars[random.randint(0,char_length-1)]
    return result

def add_contact(username,friend,pin):
    with connection.cursor() as cursor:
        sql = "select id from friends where user=%s and friend=%s"
        cursor.execute(sql,[username,friend])
        if not cursor.fetchone():
            sql = "select id from users where username=%s and pin=%s"
            print("username",friend)
            print("pin",pin)
            cursor.execute(sql,[friend,pin])
            data = cursor.fetchall()
            print(data)
            if len(data)>0:
                print("found")
                sql = "insert into friends (user,friend,channel_id,last_timestamp) values (%s,%s,%s,%s)"
                channel=randomize_channel()
                sekarang=now_utc.strftime("%Y-%m-%d %H:%M")
                cursor.execute(sql,[username,data[0][0],channel,sekarang])
                cursor.execute(sql,[data[0][0],username,channel,sekarang])
                
                sql = "insert into channels (user_id,id) values (%s,%s)"
                cursor.execute(sql,[username,channel])
                cursor.execute(sql,[data[0][0],channel])
                insert_message(channel,username,"Halo saya telah menambahkan channel ini di kontak saya!")
                return channel
            return False
        else:
            return False
        

def get_contacts(user_id):
    contacts = []
    with connection.cursor() as cursor:
        # Get all friends and their last timestamps
        sql = "SELECT friend, last_timestamp, last_message, seen, channel_id FROM friends WHERE user=%s order by last_timestamp desc"
        cursor.execute(sql, [user_id])
        data = cursor.fetchall()

        # Collect all the friend IDs from the first query
        friend_ids = [i[0] for i in data]
        
        # If there are friends, get their emails in one query
        if friend_ids:
            # Get emails for all the friends in one query to optimize performance
            sql = "SELECT id, email FROM users WHERE id IN (%s)" % ','.join(['%s'] * len(friend_ids))
            cursor.execute(sql, friend_ids)
            email_data = cursor.fetchall()
            email_dict = {email[0]: email[1] for email in email_data}  # Map friend id -> email

            # Now create the contacts list with emails
            for i in data:
                friend_id = i[0]
                last_timestamp = i[1]
                last_message = i[2]
                seen = i[3]
                channel_id=i[4]
                email = email_dict.get(friend_id, None)  # Get email, or None if not found
                contact = {'username': friend_id, 'email': email, 'last_timestamp': last_timestamp,'last_message':last_message,'seen':seen,'channel_id':channel_id}
                contacts.append(contact)                
            for i in contacts:
                i['username'] = get_user_info(i['username'])['username']
        return contacts


def get_chats(user_id,channel):
    base = ""
    with connection.cursor() as cursor:
        sql = "select id from channels where user_id=%s and id=%s"
        cursor.execute(sql,[user_id,channel])
        if (not cursor.fetchone()):
            return False

        sql = "select user_id, message, timestamp from messages where channel= %s"
        cursor.execute(sql,[channel])
        data = cursor.fetchall()
        print("user id:",user_id)

        for i in data:
            if i[0] == user_id:
                base += "<div class='message right'>"
            else:
                base += "<div class='message left'>"

            base += i[1]
            base += "<span class='timestamp'>"
            base += i[2]
            base += "</span>"
            base += "</div>"

        return base

def get_user_info(user_id):
    with connection.cursor() as cursor:
        sql = "SELECT username, email, photo_profile, pin FROM users WHERE id = %s"
        cursor.execute(sql, [user_id])
        row = cursor.fetchone()
        
        if row is None:
            raise ValueError(f"User with ID {user_id} not found.")

        username=row[0];
        email=row[1]
        photo_profile=row[2]
        pin=row[3]

        sql = "select event from events where user_id=%s"
        cursor.execute(sql,[user_id])

        return {
            'username': username,
            'email': email,
            'photo_profile': photo_profile,
            'pin': pin,
            'event': cursor.fetchall()[0][0]
        }

def check_valid_channel(channel,user_id):
    with connection.cursor() as cursor:
        sql = "select id from channels where user_id=%s and id=%s"
        cursor.execute(sql,[user_id,channel])
        return cursor.fetchone() is not None


def create_account(email, username, password):
    response = {"message":"Buat akun berhasil","valid":True,"id":-1}
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
                return response

            pin=randomize()
            sql = """
                INSERT INTO users (username, email, password, pin, photo_profile)
                VALUES (%s, %s, %s, %s, %s)
            """
            password = sha256(password.encode('utf-8')).hexdigest()
            values = [username, email, password, str(pin), "photo_profile/default.jpg"]
            cursor.execute(sql, values)
            
            sql = "select id from users where email=%s"
            cursor.execute(sql,[email])
            id_ = cursor.fetchall()
            response["id"]=id_[0][0]
            sql = "insert into events (user_id, event) values (%s,%s)"
            cursor.execute(sql,[id_[0][0],randomize_channel()])
            print(id_)

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
            length = cursor.fetchall()
            print(length)
            if (len(length)>0):
                return length[0][0]
            else:
                return -1
            
    except Exception as e:
        print(e)
