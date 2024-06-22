from fastapi import FastAPI
import uvicorn
from uuid import uuid4
from DataBaseController import DBController
from DataBaseController.DataBaseModels import Add_Student_Model_Req , Add_Teacher_Model_Req, login_user, User_Chnage_Password, User_Token, Student_Add_Attendence, User_Image_Set, User_Image_Verify
import time
from contextlib import asynccontextmanager
from LoggerUtils import configure_logger
from FaceReco import ImageComp, Task


logger = configure_logger(__name__)

config = {
    'db':'./DB/DataBase.db',
    'host':'127.0.0.1',
    'port':8000,
    'debug':True
}
dbcon:DBController = None
img_comp:ImageComp = None
@asynccontextmanager
async def lifespan(app):
    global dbcon
    global img_comp
    dbcon = DBController(config['db'])
    img_comp = ImageComp()
    logger.info(f"database is connected")
    yield
    dbcon.db_cursor.close()
    del dbcon


app = FastAPI(lifespan=lifespan)

@app.get("/")
def heartbeat()->float:
    return time.time()

@app.get("/migrate")
def make_migration():
    dbcon.make_migration()
    logger.info(f"make migration to database")
    return "DONE"


@app.post("/admin/add-student")
def add_student(request:Add_Student_Model_Req):
    ret = dbcon.add_student(request.name,request.username)
    if ret == 0:
        logger.info(f"NEW student is added with username: {request.username}")
        return {"stauts":0,"message":"student added succefully"}
    elif ret == -1:
        logger.info(f"CONSTRANT NOT STAISFY student is not added")
        return {"status":-1,"message":"constrant was not staisfy change the username"}
    else:
        logger.info(f"SOME ERROR happed while adding student {request.username}")
        return {"status":-1,"message":"unknown error happend"}
    
@app.post("/admin/add-teacher")
def add_teacher(request:Add_Teacher_Model_Req):
    ret = dbcon.add_teacher(request.name,request.username,request.subject)
    if ret == 0:
        logger.info(f"NEW teacher is added with username: {request.username} with subject: {request.subject}")
        return {"stauts":0,"message":"teacher added succefully"}
    elif ret == -1:
        logger.info(f"CONSTRANT NOT STAISFY teacher is not added")
        return {"status":-1,"message":"constrant was not staisfy chnage the username"}
    else:
        logger.info(f"ERROR teacher is not added")
        return {"status":-1,"message":"unknown error happend"}

@app.post("/user/student/teacher-list")
def teacher_list(request:User_Token):
    ret = dbcon.get_teacher_list(request.login_token)
    logger.info(f"teacher list is {ret}")
    return {"status":0,"teacher_list":ret}

@app.post("/login-student")
def login_student(request:login_user):
    ret = dbcon.login_user(0,request.username,request.password)
    if len(ret) == 0:
        logger.info(f"student is not able to login with username: {request.username}")
        return {"status":-1,"message":"token is not issused due to error in username or password","token":""}
    else:
        logger.info(f"student is able to login with username: {request.username}")
        return {"status":0,"message":"genrate token succefully","token":ret}
    
@app.post("/login-teacher")
def login_teacher(request:login_user):
    ret = dbcon.login_user(1,request.username,request.password)
    if len(ret) == 0:
        logger.info(f"teacher is not able to login with username: {request.username}")
        return {"status":-1,"message":"token is not issused due to error in username or password","token":""}
    else:
        logger.info(f"teacher is  able to login with username: {request.username}")
        return {"status":0,"message":"genrate token succefully","token":ret}

@app.post("/user/student/changepassword")
def chnagepassword(request:User_Chnage_Password):
    ret = dbcon.change_student_password(request.login_token,request.new_passowrd)
    if ret:
        logger.info(f"user login token {request.login_token} student password is  changed")
        return {"status":0,"message":"password is changed"}
    else:
        logger.info(f"user login token {request.login_token} student password is not changed")
        return {"status":-1,"message":"error happend"}

@app.post("/user/teacher/changepassword")
def chnagepassword(request:User_Chnage_Password):
    ret = dbcon.change_teacher_password(request.login_token,request.new_passowrd)
    if ret:
        logger.info(f"user login token {request.login_token} teacher password is  changed")
        return {"status":0,"message":"password is changed"}
    else:
        logger.info(f"user login token {request.login_token} teacher password is not changed")
        return {"status":-1,"message":"error happend"}


@app.post("/user/student/add-attendence")
def add_attendence(request:Student_Add_Attendence):
    if request.Signal_Strength <= -50:
        ret = dbcon.add_attendence(request.login_token,request.Teacher_id)
        
        if ret:
            logger.info(f"user login token {request.login_token} attendence is added")
            return {"status": 0,"message":"attendence is recored"}
        else:
            logger.info(f"user login token {request.login_token} attendence is not added")
            return {"status":-1,"message":"teacher token were not found"}
    else:
        logger.info(f"user login token {request.login_token} attendence is not added due to weak attendence")
        return {"status":-1,"message":"single strength is weak"}


@app.post("/user/student/put-image")
def get_image(request:User_Image_Set):
    ret = dbcon.add_image_student(request.login_token,request.image)
    if ret:
        logger.info(f"image is added with login token {request.login_token}")
        return {"status": 0,"message":"image is added"}
    else:
        logger.info(f"image is added not with login token {request.login_token}")
        return {"status": -1,"message":"some error happend"}
    
@app.post("/user/student/get-image")
def get_image(request:User_Token):
    ret = dbcon.get_image_student(request.login_token)
    if len(ret) == 0:
        logger.info(f"NOT FOUND student image not found")
        return {"status":-1,"message":"image not found in Image store","base64":""}
    else:
        logger.info(f"FOUND student image found")
        return {"status":0,"message":"Image successfully retrive from Image Store","base64":ret}

@app.post("/user/get-report")
def get_report(request:User_Token):
    ret = dbcon.make_report(request.login_token)
    if len(ret) == 0:
        logger.info(f"login problem report not found {request.login_token}")
        return {"status":0,"message":"no record were found","record":()}
    else:
        logger.info(f"report found {request.login_token}")
        return {"status":0,"message":"no record were found","record":ret}

@app.post("/user/logout")
def logout(request:User_Token):
    ret = dbcon.logout_user(request.login_token)
    if ret:
        logger.info(f"LOGOUT SUCCEFUL user with user id with token {request.login_token}")
        return {"status":0,"message":f"user associated to this token {request.login_user} is logout"}
    else:
        logger.info(f"LOGOUT UNSUCCEFUL user with user id with token {request.login_token}")
        return {"status":-1,"message":"error happend"}

@app.post("/user/student/verify-attendence")
async def verify_attendence(request:User_Image_Verify):
    ret = dbcon.get_image_student(request.login_token)
    if len(ret) == 0:
        logger.info(f"NOT FOUND student image not found")
        return {"status":-1,"message":"image not found in Image store problem in login","verified":None,"distance":None}
    else:
        logger.info(f"FOUND student image found")
        task:Task = Task(comp1=ret,comp2=request.image)
        result =  await img_comp.get_prediction(task)
        return {"status":0,"message":"Image verification happend sucessfully","verified":result['verified'],"distance":result['distance']}





if __name__ == "__main__":
    uvicorn.run('app:app',host=config['host'],port=config['port'],reload=config['debug'])