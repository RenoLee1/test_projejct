import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth, password_reset, job, log, csv_files, feedback
from app.core.config import settings
from sqlalchemy import text
from app.database.session import get_session
from app.routers import auth

app = FastAPI()

@app.on_event("startup")
def test_db_connection():
    try:
        session_generator = get_session()
        db = next(session_generator)
        db.exec(text("SELECT 1"))
        print("✅ Successfully connected to the database")
    except Exception as e:
        print("❌ Database connection failed:", e)

# Add SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=settings.SESSION_EXPIRE_MINUTES * 60
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(job.router)
app.include_router(password_reset.router)
app.include_router(log.router)
app.include_router(csv_files.router)
app.include_router(feedback.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)