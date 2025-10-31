from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.routes import info
from app.db.database import engine, Base
from app.services.crawler_service import CrawlerService

# ============================================================================
# Application entry point. Initialises database tables, starts crawler(once),
# launches fast api server
# ============================================================================

Base.metadata.create_all(bind=engine)
crawler_service = CrawlerService()

app = FastAPI(title="tehniliseintellekt.ee web chat api", version="1.0.0")
app.include_router(info.router, prefix="", tags=["info"])

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
