from fastapi import FastAPI
from app.db.database import engine
from app.db import models
from app.routes import signup_routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(signup_routes.router)