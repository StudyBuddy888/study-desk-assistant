from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
import datetime
import jwt

app = FastAPI()

# ✅ Add CORS Middleware to Allow Requests from Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# MongoDB Connection
MONGO_URI = ""
client = MongoClient(MONGO_URI)
db = client["study_tracker"]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Secret Key
SECRET_KEY = "your-secret-key"

# User Model
class User(BaseModel):
    username: str
    email: str
    password: str

# Session Model
class StudySession(BaseModel):
    user_email: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    distractions: int = 0
    completed: bool = False

# 🔹 1️⃣ Register User
@app.post("/register")
async def register_user(request: Request):
    try:
        user = await request.json()  # Read JSON properly

        if not all(key in user for key in ["username", "email", "password"]):
            raise HTTPException(status_code=400, detail="Missing fields")

        if db.users.find_one({"email": user["email"]}):
            raise HTTPException(status_code=400, detail="Email already exists")

        hashed_password = pwd_context.hash(user["password"])
        user_data = {"username": user["username"], "email": user["email"], "password": hashed_password}
        db.users.insert_one(user_data)

        return {"message": "User registered successfully"}
    
    except Exception as e:
        print("Error:", str(e))  # Log the actual error
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 2️⃣ Login User
@app.post("/login")
async def login_user(request: Request):
    try:
        user = await request.json()
        db_user = db.users.find_one({"email": user["email"]})

        if not db_user or not pwd_context.verify(user["password"], db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode({"email": user["email"]}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        print("Login Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 3️⃣ Start a Study Session
@app.post("/start-session")
async def start_session(request: Request):
    try:
        session = await request.json()

        if not all(key in session for key in ["user_email", "start_time", "end_time"]):
            raise HTTPException(status_code=400, detail="Missing fields in session data")

        db.study_sessions.insert_one(session)
        return {"message": "Study session started", "session": session}

    except Exception as e:
        print("Session Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 4️⃣ Get Study Progress
@app.get("/progress/{email}")
async def get_progress(email: str):
    try:
        sessions = list(db.study_sessions.find({"user_email": email}, {"_id": 0}))

        if not sessions:
            raise HTTPException(status_code=404, detail="No study sessions found")

        return {"study_sessions": sessions}

    except Exception as e:
        print("Progress Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# 🔹 5️⃣ API Status
@app.get("/")
def home():
    return {"message": "Study Desk Assistant API is running!"}
