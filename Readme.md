# This is API for FaceMat backend
- for running the API follow the following steps:
    ```shell
        python3 -m venv env
    
        # for windows
        .\env\Scripts\activate
        pip install -r req.txt
        
        python3 app.py     

    ```
    note: if you face any error then use python3

- for docs go to http://127.0.0.1:8000/docs here you get details on every end point for intergration


Sure, here is a detailed documentation for the API described in your code. This documentation includes descriptions of each endpoint, their methods, request payloads, and expected responses.

---

## FastAPI Application Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Lifespan Management
This API uses an async lifespan to initialize and clean up resources such as database connections and image processing components.

---

### Endpoints

#### 1. Heartbeat
**Endpoint:** `/`  
**Method:** `GET`  
**Description:** Returns the current server time to check if the server is running.

**Response:**
- `200 OK`: Returns the current time as a float.
```json
{
  "current_time": 1622470426.892374
}
```

---

#### 2. Database Migration
**Endpoint:** `/migrate`  
**Method:** `GET`  
**Description:** Initiates database migration.

**Response:**
- `200 OK`: Returns a message indicating the migration status.
```json
{
  "message": "DONE"
}
```

---

#### 3. Add Student
**Endpoint:** `/admin/add-student`  
**Method:** `POST`  
**Description:** Adds a new student to the database.

**Request Body:**
- `Add_Student_Model_Req` (JSON)
```json
{
  "name": "string",
  "username": "string"
}
```

**Response:**
- `200 OK`: Returns the status of the student addition.
```json
{
  "status": 0,
  "message": "student added successfully"
}
```
or
```json
{
  "status": -1,
  "message": "constraint was not satisfied; change the username"
}
```

---

#### 4. Add Teacher
**Endpoint:** `/admin/add-teacher`  
**Method:** `POST`  
**Description:** Adds a new teacher to the database.

**Request Body:**
- `Add_Teacher_Model_Req` (JSON)
```json
{
  "name": "string",
  "username": "string",
  "subject": "string"
}
```

**Response:**
- `200 OK`: Returns the status of the teacher addition.
```json
{
  "status": 0,
  "message": "teacher added successfully"
}
```
or
```json
{
  "status": -1,
  "message": "constraint was not satisfied; change the username"
}
```

---

#### 5. Teacher List
**Endpoint:** `/user/student/teacher-list`  
**Method:** `POST`  
**Description:** Retrieves the list of teachers for a student.

**Request Body:**
- `User_Token` (JSON)
```json
{
  "login_token": "string"
}
```

**Response:**
- `200 OK`: Returns the list of teachers.
```json
{
  "status": 0,
  "teacher_list": ["teacher1", "teacher2", "teacher3"]
}
```

---

#### 6. Login Student
**Endpoint:** `/login-student`  
**Method:** `POST`  
**Description:** Authenticates a student and generates a login token.

**Request Body:**
- `login_user` (JSON)
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- `200 OK`: Returns the login token if authentication is successful.
```json
{
  "status": 0,
  "message": "generate token successfully",
  "token": "string"
}
```
or
```json
{
  "status": -1,
  "message": "token is not issued due to error in username or password",
  "token": ""
}
```

---

#### 7. Login Teacher
**Endpoint:** `/login-teacher`  
**Method:** `POST`  
**Description:** Authenticates a teacher and generates a login token.

**Request Body:**
- `login_user` (JSON)
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- `200 OK`: Returns the login token if authentication is successful.
```json
{
  "status": 0,
  "message": "generate token successfully",
  "token": "string"
}
```
or
```json
{
  "status": -1,
  "message": "token is not issued due to error in username or password",
  "token": ""
}
```

---

#### 8. Change Student Password
**Endpoint:** `/user/student/changepassword`  
**Method:** `POST`  
**Description:** Changes the password for a student.

**Request Body:**
- `User_Chnage_Password` (JSON)
```json
{
  "login_token": "string",
  "new_password": "string"
}
```

**Response:**
- `200 OK`: Returns the status of the password change.
```json
{
  "status": 0,
  "message": "password is changed"
}
```
or
```json
{
  "status": -1,
  "message": "error happened"
}
```

---

#### 9. Change Teacher Password
**Endpoint:** `/user/teacher/changepassword`  
**Method:** `POST`  
**Description:** Changes the password for a teacher.

**Request Body:**
- `User_Chnage_Password` (JSON)
```json
{
  "login_token": "string",
  "new_password": "string"
}
```

**Response:**
- `200 OK`: Returns the status of the password change.
```json
{
  "status": 0,
  "message": "password is changed"
}
```
or
```json
{
  "status": -1,
  "message": "error happened"
}
```

---

#### 10. Add Attendance
**Endpoint:** `/user/student/add-attendence`  
**Method:** `POST`  
**Description:** Adds attendance for a student.

**Request Body:**
- `Student_Add_Attendence` (JSON)
```json
{
  "login_token": "string",
  "Teacher_id": "string",
  "Signal_Strength": "int"
}
```

**Response:**
- `200 OK`: Returns the status of the attendance addition.
```json
{
  "status": 0,
  "message": "attendance is recorded"
}
```
or
```json
{
  "status": -1,
  "message": "signal strength is weak"
}
```

---

#### 11. Upload Student Image
**Endpoint:** `/user/student/put-image`  
**Method:** `POST`  
**Description:** Uploads an image for a student.

**Request Body:**
- `User_Image_Set` (JSON)
```json
{
  "login_token": "string",
  "image": "base64string"
}
```

**Response:**
- `200 OK`: Returns the status of the image upload.
```json
{
  "status": 0,
  "message": "image is added"
}
```
or
```json
{
  "status": -1,
  "message": "some error happened"
}
```

---

#### 12. Retrieve Student Image
**Endpoint:** `/user/student/get-image`  
**Method:** `POST`  
**Description:** Retrieves a student's image.

**Request Body:**
- `User_Token` (JSON)
```json
{
  "login_token": "string"
}
```

**Response:**
- `200 OK`: Returns the student's image in base64 format.
```json
{
  "status": 0,
  "message": "image successfully retrieved",
  "base64": "base64string"
}
```
or
```json
{
  "status": -1,
  "message": "image not found",
  "base64": ""
}
```

---

#### 13. Generate Report
**Endpoint:** `/user/get-report`  
**Method:** `POST`  
**Description:** Generates a report for the user.

**Request Body:**
- `User_Token` (JSON)
```json
{
  "login_token": "string"
}
```

**Response:**
- `200 OK`: Returns the report.
```json
{
  "status": 0,
  "message": "report generated",
  "record": "report data"
}
```
or
```json
{
  "status": -1,
  "message": "no records found",
  "record": []
}
```

---

#### 14. Logout
**Endpoint:** `/user/logout`  
**Method:** `POST`  
**Description:** Logs out the user by invalidating the login token.

**Request Body:**
- `User_Token` (JSON)
```json
{
  "login_token": "string"
}
```

**Response:**
- `200 OK`: Returns the status of the logout.
```json
{
  "status": 0,
  "message": "user logged out"
}
```
or
```json
{
  "status": -1,
  "message": "error happened"
}
```

---

#### 15. Verify Attendance
**Endpoint:** `/user/student/verify-attendence`  
**Method:** `POST`  
**Description:** Verifies a student's attendance using image recognition.

**Request Body:**
- `User_Image_Verify` (JSON)
```json
{
  "login_token": "string",
  "image": "base64string"
}
```

**Response:**
- `200 OK`: Returns the verification status and the distance metric.
```json
{
  "status": 0,
  "message

": "image verification successful",
  "verified": "boolean",
  "distance": "float"
}
```
or
```json
{
  "status": -1,
  "message": "image not found",
  "verified": null,
  "distance": null
}
```

---

### Running the Application
To run the application, use the following command:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

### Configuration
- **Database Path:** `./DB/DataBase.db`
- **Host:** `127.0.0.1`
- **Port:** `8000`
- **Debug Mode:** `True`

---

This documentation covers the available endpoints, request and response formats, and additional configuration details for running the application. If you have any further questions or need additional details, feel free to ask!