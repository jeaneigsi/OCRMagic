# Import required FastAPI classes for API routing, file handling, and HTTP exception management
from fastapi import APIRouter, File, UploadFile, HTTPException, status,Depends
from fastapi.responses import JSONResponse

# Image processing and OCR model imports
from PIL import Image
import io
from typing import List

# Custom OCR imports from the Surya package
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
from models.secure.auth_baerer import JWTBearer

# Utility functions for memory management and image processing
from utils import overall_memory_usage, process, reduce_image_size

# Settings and additional imports
from surya.settings import settings
import torch
import gc

# Supported languages for OCR
langs = ["fr", "en"]  # Customize based on required OCR languages

# Initialize the FastAPI router for organizing endpoints
router = APIRouter()

@router.post("/inference", response_model=List[str], dependencies=[Depends(JWTBearer())])
async def inference(file: UploadFile = File(...)):
    """
    Perform OCR on the uploaded image file and return recognized text.
    
    Args:
        file (UploadFile): The image file to be processed.

    Returns:
        JSONResponse: Recognized text lines from the image in JSON format.
    """
    try:
        # Validate that a file is provided
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No file uploaded."
            )

        # Open and resize the uploaded image to optimize processing
        doc = Image.open(io.BytesIO(await file.read()))
        doc = reduce_image_size(doc, reduction_factor=0.7)

        # Load OCR detection and recognition models
        det_model, det_processor = load_det_model(dtype=torch.float16), load_det_processor()
        rec_model, rec_processor = load_rec_model(dtype=torch.float16), load_rec_processor()

        # Run the OCR pipeline on the processed image
        predictions = run_ocr([doc], [langs], det_model, det_processor, rec_model, rec_processor)
        
        # Extract and process text from predictions
        results = process(predictions)
        
        # Unload the models to free memory after processing
        unload(det_model, det_processor, rec_model, rec_processor)
        
        # Structure results in a dictionary for JSON response
        result = {
            "rec_text": results
        }

        return JSONResponse(content=result)

    except Exception as e:
        # Catch and report errors with HTTP 500 status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )


def unload(det_model, det_processor, rec_model, rec_processor):
    """
    Free up memory by unloading models and processors.
    
    Args:
        det_model: Detection model to unload.
        det_processor: Processor for the detection model.
        rec_model: Recognition model to unload.
        rec_processor: Processor for the recognition model.
    """
    del det_model, det_processor, rec_model, rec_processor
    gc.collect()


def process(prediction):
    """
    Process OCR predictions to extract text lines.
    
    Args:
        prediction: OCR output to be processed.

    Returns:
        list: A list of extracted text lines from the image.
    """
    output = []
    for ocr_result in prediction:
        # Loop through each text line in the OCR result and append to output list
        for text_line in ocr_result.text_lines:
            output.append(text_line.text)
        
        # Log memory usage to monitor resource consumption
        overall_memory_usage()
        
    return output
