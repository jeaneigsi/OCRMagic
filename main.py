from fastapi import FastAPI, UploadFile, HTTPException, Request,File,APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from paddlex import create_pipeline
from PIL import Image
import numpy as np
import os
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
from paddlex import create_pipeline
import io
import json
from typing import Union, List
from models.paddle.router import router as paddle_router
from models.surya.router import router as surya_router
from models.secure.api import router as secure_router
from dotenv import load_dotenv
from pathlib import Path
from fastapi_utils.tasks import repeat_every


load_dotenv()

# Parse ALLOWED_ORIGINS from environment variable
# allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")



app = FastAPI(openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")
app.mount("/static", StaticFiles(directory="static"), name="static")

# router = APIRouter()

folder_path = Path("./ouput")


templates = Jinja2Templates(directory="templates")
# logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Use parsed list from environment
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Adjust as needed
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(paddle_router, prefix="/api/v1/paddle-ocr", tags=["Paddle OCR"])
app.include_router(surya_router, prefix="/api/v1/surya-ocr", tags=["Surya OCR"])
app.include_router(secure_router, prefix="/api/v1/secure-ocr", tags=["O2th"])



@app.get("/")
async def home(request : Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.on_event("startup")
@repeat_every(seconds=10)  # Adjust as needed
async def monitor_folder():
    files = list(folder_path.glob("*"))  # List all files in the folder
    if len(files) > 2:  # Check if there are more than 2 files
        for file in files:
            file.unlink()  # Delete each file
            print(f"Deleted file: {file.name}")

async def startup_event():
    await monitor_folder()