from fastapi import FastAPI
from app.routes.claims import router as claims_router
from app.routes.chat import router as chat_router

app = FastAPI(
    title="ClaimForge Edge Simple Backend",
    version="1.0.0"
)

app.include_router(claims_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
