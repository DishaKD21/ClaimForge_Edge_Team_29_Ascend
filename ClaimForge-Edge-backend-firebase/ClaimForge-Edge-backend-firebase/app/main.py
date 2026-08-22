from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app=FastAPI(title="ClaimForge Edge Backend",version="1.0.0",description="Firebase + Hugging Face backend for AI insurance claim verification.")
origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root(): return {"service":"ClaimForge Edge","status":"ok","docs":"/docs"}

@app.get("/health")
def health(): return {"status":"ok"}
