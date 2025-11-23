from fastapi import FastAPI
from .routes import router

app = FastAPI(title="SafeOps LogParser")

app.include_router(router, prefix="/logs")

import os
from pymongo import MongoClient

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    app.database = app.mongodb_client["safeops-logminer"]
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "LogParser Service is running"}


