from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
import datetime
import jwt
from bson import ObjectId

app = FastAPI()

# ✅ CORS Middleware (Allow Frontend Requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust if deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB Connection
MONGO_URI = "mongodb+srv://vishalgaonkar2004:gaonkar2004@cluster0.s4nkd.mongodb.net"
client = MongoClient(MONGO_URI)
db = client["study_tracker"]

# ✅ Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ JWT Secret Key
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# ✅ User Model
class User(BaseModel):
    username: str
    email: str
    password: str

# ✅ Task Model
class TaskList(BaseModel):
    user_email: str
    task_schedule: datetime.datetime
    task: str
    status: str = "pending"  # Default status

# ✅ Helper function to verify token & extract user email
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 🔹 1️⃣ Register User
@app.post("/register")
async def register_user(user: User):
    try:
        # Check if user already exists
        if db.users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = pwd_context.hash(user.password)
        user_data = {"username": user.username, "email": user.email, "password": hashed_password}
        db.users.insert_one(user_data)

        return {"message": "User registered successfully!"}

    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 2️⃣ Login User (Returns JWT Token)
@app.post("/login")
async def login_user(request: Request):
    try:
        user = await request.json()
        db_user = db.users.find_one({"email": user["email"]})

        if not db_user or not pwd_context.verify(user["password"], db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode({"email": user["email"]}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        print("Login Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 3️⃣ Add Task (Authenticated)
@app.post("/add-task")
async def add_task(request: Request):
    try:
        data = await request.json()
        token = data.get("token")

        if not token:
            raise HTTPException(status_code=401, detail="Missing authentication token")

        user_email = verify_token(token)

        if not all(key in data for key in ["task_schedule", "task", "status"]):
            raise HTTPException(status_code=400, detail="Missing task fields")

        task_data = {
            "user_email": user_email,
            "task_schedule": data["task_schedule"],
            "task": data["task"],
            "status": data["status"],
        }
        
        db.tasks.insert_one(task_data)
        return {"message": "Task added successfully", "task": task_data}

    except Exception as e:
        print("Task Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 4️⃣ Get User's Tasks (Authenticated)
@app.get("/tasks")
async def get_tasks(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or "Bearer " not in auth_header:
            raise HTTPException(status_code=401, detail="Missing authentication token")

        token = auth_header.split("Bearer ")[1]
        user_email = verify_token(token)

        tasks = list(db.tasks.find({"user_email": user_email}, {"_id": 1, "task_schedule": 1, "task": 1, "status": 1}))

        for task in tasks:
            task["_id"] = str(task["_id"])  # Convert ObjectId to string

        return {"tasks": tasks}

    except Exception as e:
        print("Task Fetch Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 5️⃣ Update Task Status (Authenticated)
@app.put("/update-task/{task_id}")
async def update_task(task_id: str, request: Request):
    try:
        data = await request.json()
        token = data.get("token")

        if not token:
            raise HTTPException(status_code=401, detail="Missing authentication token")

        user_email = verify_token(token)

        if "status" not in data:
            raise HTTPException(status_code=400, detail="Missing status field")

        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task or task["user_email"] != user_email:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": data["status"]}})
        return {"message": "Task updated successfully"}

    except Exception as e:
        print("Task Update Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 6️⃣ Delete Task (Authenticated)
@app.delete("/delete-task/{task_id}")
async def delete_task(task_id: str, request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or "Bearer " not in auth_header:
            raise HTTPException(status_code=401, detail="Missing authentication token")

        token = auth_header.split("Bearer ")[1]
        user_email = verify_token(token)

        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task or task["user_email"] != user_email:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        db.tasks.delete_one({"_id": ObjectId(task_id)})
        return {"message": "Task deleted successfully"}

    except Exception as e:
        print("Task Delete Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 7️⃣ API Status
@app.get("/")
def home():
    return {"message": "Study Desk Assistant API is running!"}
