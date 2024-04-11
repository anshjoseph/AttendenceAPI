import sqlite3
from sqlite3 import IntegrityError
from uuid import uuid4
from hashlib import sha256
# import zlib

class DBController:
   
    def __init__(self,path:str) -> None:
        self.path = path
        self.db_connection= sqlite3.connect(self.path,check_same_thread=False)
        self.db_cursor = self.db_connection.cursor()
    def make_migration(self):
        self.db_cursor.execute("CREATE TABLE if not exists Students(id text unique, username text unique, name text, password text)")
        self.db_cursor.execute("CREATE TABLE if not exists Teachers(id text unique, username text unique, name text, subject text, password text)")
        self.db_cursor.execute("CREATE TABLE if not exists Attendence_Record(id text unique, te_id text, st_id text, datetime real)")
        self.db_cursor.execute("CREATE TABLE if not exists Login_Token(id text unique, user_id text unique, datetime real, login_type int)")
        self.db_cursor.execute("CREATE TABLE if not exists ImageStore(id text unique, user_id text ,data text)")


    def add_login_token(self,user_id:str,login_type:int):
        login_token  = str(uuid4())
        try:
            self.db_cursor.execute(f"DELETE FROM Login_Token where user_id = '{user_id}'")
            self.db_cursor.execute(f"INSERT INTO Login_Token(id,user_id,datetime,login_type) VALUES ('{login_token}','{user_id}',julianday('now'),{login_type})")
            self.db_connection.commit()
            return login_token
        except Exception as e:
            return ""
        
    def login_user(self,login_type:int,username:str,password:str):
        password = sha256(password.encode()).hexdigest()
        # login_type 0 : student, login_type 1: teacher
        if login_type == 0:
            data = self.db_cursor.execute(f"SELECT id,password FROM Students WHERE username = '{username}'")
            data = data.fetchall()[0]
            if data[1] == password:
                return self.add_login_token(data[0],0)
            else:
                return ""
        elif login_type == 1:
            data = self.db_cursor.execute(f"SELECT id,password FROM Teachers WHERE username = '{username}'")
            data = data.fetchall()[0]
            if data[1] == password:
                return self.add_login_token(data[0],1)
            else:
                return ""
    def logout_user(self,login_token:str):
        try:
            self.db_cursor.execute(f"DELETE FROM Login_Token where id = '{login_token}'")
            self.db_connection.commit()
            return True
        except:
            return False
        
    def check_login(self,login_token:str):
        data = self.db_cursor.execute(f"SELECT user_id, login_type FROM Login_Token where id = '{login_token}'").fetchall()
        if len(data) >= 1:
            return (True,data[0][0],data[0][1])
        else:
            return (False,"",-1)

    def add_teacher(self,name:str,username:str,subject:str):
        default_password = '12345678'
        default_password_hash = sha256(default_password.encode()).hexdigest()
        try:
            self.db_cursor.execute(f"INSERT INTO Teachers(id,username,name,subject,password) VALUES ('{uuid4()}','{username}','{name}', '{subject}','{default_password_hash}')")
            self.db_connection.commit()
            return 0
        except Exception as e:
            if type(e) == IntegrityError:
                return -1
            return -40

    def change_teacher_password(self,login_token:str,password:str):
        password = sha256(password.encode()).hexdigest()
        ch_login = self.check_login(login_token)
        if ch_login[0]:
            self.db_cursor.execute(f"UPDATE Teachers SET password='{password}' Where id ='{ch_login[1]}'")
            return True
        else:
            return False
    
    def add_student(self,name:str,username:str):
        default_password = '12345678'
        default_password_hash = sha256(default_password.encode()).hexdigest()
        try:
            self.db_cursor.execute(f"INSERT INTO Students(id,username,name,password) VALUES ('{uuid4()}','{username}','{name}','{default_password_hash}')")
            self.db_connection.commit()
            return 0
        except Exception as e:
            if type(e) == IntegrityError:
                return -1
            return -40

    def change_student_password(self,login_token:str,password:str):
        password = sha256(password.encode()).hexdigest()
        ch_login = self.check_login(login_token)
        print(ch_login)
        if ch_login[0]:
            self.db_cursor.execute(f"UPDATE Students SET password='{password}' Where id ='{ch_login[1]}'")
            return True
        else:
            return False
    
    def get_teacher_list(self,login_token:str):
        ch_login = self.check_login(login_token)
        if ch_login[0]:
            return self.db_cursor.execute("SELECT id, name, subject FROM Teachers").fetchall()
        else:
            return ()
    # TODO: add compression method
    def add_image_student(self,login_token:str,image:bytes):
        ch_login = self.check_login(login_token)
        if ch_login[0]:
            self.db_cursor.execute(f"DELETE FROM ImageStore where user_id = '{ch_login[1]}'")
            self.db_cursor.execute(f"INSERT INTO ImageStore(id,user_id,data) VALUES ('{uuid4()}','{ch_login[1]}','{image.decode()}')")
            self.db_connection.commit()
            return True
        else:
            return False
    def get_image_student(self,login_token:str):
        ch_login = self.check_login(login_token)
        if ch_login[0]:
            images = self.db_cursor.execute(f"SELECT data FROM ImageStore where user_id = '{ch_login[1]}'").fetchall()[0][0]
            return images
        else:
            return ""
    def add_attendence(self,login_token:str,te_id:str):
        ch_login = self.check_login(login_token)
        try:
            if len(self.db_cursor.execute(f"SELECT id FROM Teachers where id = '{te_id}'").fetchall()) == 1 and ch_login[0]:
                self.db_cursor.execute(f"INSERT INTO Attendence_Record(id,te_id,st_id,datetime) VALUES ('{uuid4()}','{te_id}','{ch_login[1]}',julianday('now','localtime'))")
                self.db_connection.commit()
                return True
            else:
                return False
        except Exception as e:
            return False
    def make_report(self,login_token:str):
        ch_login = self.check_login(login_token)
        # 0 for student and 1 for teacher
        if ch_login[0] and ch_login[2] == 0:
            data = self.db_cursor.execute(f"SELECT strec.id, Teachers.subject, strec.name, date(strec.datetime), time(strec.datetime) FROM (SELECT * FROM (SELECT Attendence_Record.id,st_id,te_id,name,datetime FROM Attendence_Record INNER JOIN Students ON Attendence_Record.st_id = Students.id ) as st WHERE st.st_id = '{ch_login[1]}') as strec INNER JOIN Teachers ON strec.te_id = Teachers.id ").fetchall()
            return data
        elif ch_login[0] and ch_login[2] == 1:
            data = self.db_cursor.execute(f"SELECT strec.id, Teachers.subject, strec.name, date(strec.datetime), time(strec.datetime) FROM (SELECT * FROM (SELECT Attendence_Record.id,st_id,te_id,name,datetime FROM Attendence_Record INNER JOIN Students ON Attendence_Record.st_id = Students.id ) as st WHERE st.te_id = '{ch_login[1]}') as strec INNER JOIN Teachers ON strec.te_id = Teachers.id ").fetchall()
            return data