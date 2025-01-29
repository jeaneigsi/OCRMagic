# FastAPI imports for API routing, file handling, and exception management
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Body, Depends
from fastapi.responses import JSONResponse

# Utility functions for image processing
from utils import pil_to_np, reduce_image_size

# Libraries for image manipulation, pipeline creation, and JSON handling
from PIL import Image
import io
from paddlex import create_pipeline
import os
import json
import gc
from typing import List

# Authentication model import
from models.secure.auth_baerer import JWTBearer

pipeline = create_pipeline(pipeline="OCR", device="cpu")

# Initialize FastAPI router
router = APIRouter()

# Endpoint for single image OCR processing
@router.post("/ocr")
async def ocr_pipeline(file: UploadFile = File(...)):
    # Set up the OCR pipeline with specified device
    
    
    try:
        # Read and process the uploaded image
        img_bytes = await file.read()
        name, _ = os.path.splitext(file.filename)
        print(f"Received file: {file.filename}, size: {len(img_bytes)} bytes")
        
        # Convert to PIL image and resize to optimize processing
        # img = Image.open(io.BytesIO(img_bytes))
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        img = reduce_image_size(img, reduction_factor=0.7)
        image_np = pil_to_np(img)
       

        # Perform OCR prediction
        output = pipeline.predict(image_np)
        
        # Collect and store OCR results in JSON format
        for res in output:
            res.print()
            res.save_to_json(f"./output/{name}.json")
            with open(f"./output/{name}.json", 'r') as doc:
                data = json.load(doc)
               

        # Free up memory by unloading the pipeline
        unload(pipeline)

        return JSONResponse(content=data)

    except Exception as e:
        # Return error details in case of failure
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.post("/ocr_secure", dependencies=[Depends(JWTBearer())])
async def ocr_pipeline(file: UploadFile = File(...)):
    # Set up the OCR pipeline with specified device
    
    
    try:
        # Read and process the uploaded image
        img_bytes = await file.read()
        name, _ = os.path.splitext(file.filename)
        print(f"Received file: {file.filename}, size: {len(img_bytes)} bytes")
        
        # Convert to PIL image and resize to optimize processing
        img = Image.open(io.BytesIO(img_bytes))
        img = reduce_image_size(img, reduction_factor=0.7)
        image_np = pil_to_np(img)
       

        # Perform OCR prediction
        output = pipeline.predict(image_np)
        
        # Collect and store OCR results in JSON format
        for res in output:
            res.print()
            res.save_to_json(f"./output/{name}.json")
            with open(f"./output/{name}.json", 'r') as doc:
                data = json.load(doc)
               

        # Free up memory by unloading the pipeline
        unload(pipeline)

        return JSONResponse(content=data)

    except Exception as e:
        # Return error details in case of failure
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# Endpoint for batch image OCR processing
@router.post("/ocr_batch", dependencies=[Depends(JWTBearer())])
async def ocr_batch_pipeline(images: List[UploadFile] = File(...)):
    try:
        results = []
        # Initialize the OCR pipeline
        pipeline = create_pipeline(pipeline="OCR", device="cpu")

        # Process each image in the uploaded batch
        for image in images:
            img_bytes = await image.read()
            name, _ = os.path.splitext(image.filename)
            print(f"Received file: {image.filename}, size: {len(img_bytes)} bytes")
            
            # Convert to PIL image and resize to optimize processing
            img = Image.open(io.BytesIO(img_bytes))
            img = reduce_image_size(img, reduction_factor=0.7)
            image_np = pil_to_np(img)

            # Perform OCR prediction on each image
            output = pipeline.predict(image_np)
            
            # Collect and store OCR results for each image
            for res in output:
                res.print()
                res.save_to_json(f"./output/{name}.json")
                with open(f"./output/{name}.json", 'r') as file:
                    data = json.load(file)
                    results.append(data)

        # Free up memory by unloading the pipeline after batch processing
        unload(pipeline)

        return JSONResponse(content=results)

    except Exception as e:
        # Return error details in case of failure
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")


# Helper function to release pipeline resources and trigger garbage collection
def unload(pipeline):
    del pipeline
    gc.collect()
