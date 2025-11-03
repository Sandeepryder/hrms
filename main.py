from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from sqlalchemy import text


app = FastAPI(title="AI Recruitment API")

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Recruitment AI module running 🚀"}


@app.on_event("startup")
def startup_event():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")) 
        print("✅ Database connected successfully")
        Base.metadata.create_all(bind=engine)

    except Exception as e:
        print("❌ Database connection failed:", e)


@app.on_event("shutdown")
def shutdown_event():
    engine.dispose()
    print("🛑 Database connection pool closed")

# ✅ Include all routes
app.include_router(router)
