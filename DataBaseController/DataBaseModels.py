from pydantic import BaseModel



class Add_Student_Model_Req(BaseModel):
    name:str
    username:str

class Add_Teacher_Model_Req(BaseModel):
    name:str
    username:str
    subject:str

class login_user(BaseModel):
    username:str
    password:str

class User_Chnage_Password(BaseModel):
    login_token:str
    new_passowrd:str

class User_Token(BaseModel):
    login_token:str

class Student_Add_Attendence(BaseModel):
    login_token:str
    Signal_Strength:int
    Teacher_id:str

class User_Image_Set(BaseModel):
    login_token:str
    image:str

class User_Image_Verify(BaseModel):
    login_token:str
    image:str