from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.database import Base, engine
from app.models import Check, CheckPhoto, PhotoDamage, RentalContract, User, Vehicle  # noqa: F401
from app.routes.auth import router as auth_router
from app.routes.check import router as check_router
from app.routes.check_photo import router as check_photo_router
from app.routes.contracts import router as contracts_router
from app.routes.signature import router as signature_router
from app.routes.upload import router as upload_router
from app.routes.user import router as user_router
from app.routes.vehicle import router as vehicle_router



app = FastAPI(title=settings.app_name)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ton-front.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected and tables created.")
    except Exception as error:
        print("⚠️ Database unavailable on startup.")
        print(f"Error: {error}")


app.include_router(vehicle_router)
app.include_router(check_router)
app.include_router(check_photo_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(signature_router)
app.include_router(contracts_router)

@app.get("/")
def read_root():
    return {
        "message": f"Bienvenue sur {settings.app_name}",
        "environment": settings.app_env,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-test")
def test_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as error:
        return {
            "database": "disconnected",
            "error": str(error),
        }