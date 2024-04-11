from fastapi import FastAPI
import uvicorn
from uuid import uuid4
from DataBaseController import DBController
from DataBaseController.DataBaseModels import Add_Student_Model_Req , Add_Teacher_Model_Req, login_user, User_Chnage_Password, User_Token, Student_Add_Attendence, User_Image_Set
import time

app = FastAPI()
config = {
    'db':'./DB/DataBase.db',
    'host':'127.0.0.1',
    'port':8000,
    'debug':True
}
dbcon = DBController(config['db'])


# test code

@app.get("/")
def heartbeat()->float:
    return time.time()

@app.get("/migrate")
def make_migration():
    dbcon.make_migration()
    return "DONE"


@app.post("/admin/add-student")
def add_student(request:Add_Student_Model_Req):
    ret = dbcon.add_student(request.name,request.username)
    if ret == 0:
        return {"stauts":0,"message":"student added succefully"}
    elif ret == -1:
        return {"status":-1,"message":"constrant was not staisfy chnage the username"}
    else:
        return {"status":-1,"message":"unknown error happend"}
@app.post("/admin/add-teacher")
def add_teacher(request:Add_Teacher_Model_Req):
    ret = dbcon.add_teacher(request.name,request.username,request.subject)
    if ret == 0:
        return {"stauts":0,"message":"teacher added succefully"}
    elif ret == -1:
        return {"status":-1,"message":"constrant was not staisfy chnage the username"}
    else:
        return {"status":-1,"message":"unknown error happend"}

@app.post("/user/student/teacher-list")
def teacher_list(request:User_Token):
    ret = dbcon.get_teacher_list(request.login_token)
    return {"status":0,"teacher_list":ret}

@app.post("/login-student")
def login_student(request:login_user):
    ret = dbcon.login_user(0,request.username,request.password)
    if len(ret) == 0:
        return {"status":-1,"message":"token is not issused due to error in username or password","token":""}
    else:
        return {"status":0,"message":"genrate token succefully","token":ret}
@app.post("/login-teacher")
def login_teacher(request:login_user):
    ret = dbcon.login_user(1,request.username,request.password)
    if len(ret) == 0:
        return {"status":-1,"message":"token is not issused due to error in username or password","token":""}
    else:
        return {"status":0,"message":"genrate token succefully","token":ret}

@app.post("/user/student/changepassword")
def chnagepassword(request:User_Chnage_Password):
    ret = dbcon.change_student_password(request.login_token,request.new_passowrd)
    if ret:
        return {"status":0,"message":"password is changed"}
    else:
        return {"status":-1,"message":"error happend"}

@app.post("/user/teacher/changepassword")
def chnagepassword(request:User_Chnage_Password):
    ret = dbcon.change_teacher_password(request.login_token,request.new_passowrd)
    if ret:
        return {"status":0,"message":"password is changed"}
    else:
        return {"status":-1,"message":"error happend"}

@app.post("/user/student/add-attendence")
def add_attendence(request:Student_Add_Attendence):
    if request.Signal_Strength <= -50:
        ret = dbcon.add_attendence(request.login_token,request.Teacher_id)
        if ret:
            return {"status": 0,"message":"attendence is recored"}
        else:
            return {"status":-1,"message":"teacher token were not found"}
    else:
        return {"status":-1,"message":"single strength is weak"}


@app.post("/user/student/put-image")
def get_image(request:User_Image_Set):
    ret = dbcon.add_image_student(request.login_token,request.image)
    if ret:
        return {"status": 0,"message":"image is added"}
    else:
        return {"status": -1,"message":"some error happend"}
@app.post("/user/student/get-image")
def get_image(request:User_Token):
    ret = dbcon.get_image_student(request.login_token)
    if len(ret) == 0:
        return {"status":-1,"message":"image not found in Image store","base64":""}
    else:
        return {"status":0,"message":"Image successfully retrive from Image Store","base64":ret}

@app.post("/user/get-report")
def get_report(request:User_Token):
    ret = dbcon.make_report(request.login_token)
    if len(ret) == 0:
        return {"status":0,"message":"no record were found","record":()}
    else:
        return {"status":0,"message":"no record were found","record":ret}

@app.post("/user/logout")
def logout(request:User_Token):
    ret = dbcon.logout_user(request.login_token)
    if ret:
        return {"status":0,"message":f"user associated to this token {login_user} is logout"}
    else:
        return {"status":-1,"message":"error happend"}







if __name__ == "__main__":
    uvicorn.run('app:app',host=config['host'],port=config['port'],reload=config['debug'])