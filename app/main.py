from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.routes import auth, cmt
from app.db.database import engine
from app.db.models import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI JWT Auth", version="1.0.0")
app.include_router(cmt.router, prefix="/api/cmt", tags=["cmt"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}