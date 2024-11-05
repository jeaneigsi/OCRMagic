# Modular OCR API Repository

This repository serves as a modular base for OCR tasks. Feel free to improve it and share your feedback ⭐

## Repository Structure

```plaintext
.
├── main.py
├── input/
└── models/        # Add your new models here
```
At first load, app download models weights, so wait a bit before to  ready. *Use paddle for speed and surya for accuracy*

## API Endpoints

All routes are secured with JWT authentication and can be accessed via the following endpoints:

```plaintext
/                    # UI for the OCR API
/api/v1/paddle-ocr   # Run inference with PaddleOCR
/api/v1/surya-ocr    # Run inference with SuryaOCR
```

## Access Token Requirement  

You need to obtain an access token before running any inference.
Only file uploads are supported for inference.
Use the batch endpoint to perform inference on multiple images within a folder.

## Authentication Endpoints   

Generate your access token, add bearer authentication, and proceed with inference requests:

```bash
/user/login: Log in if you already have an access token
/user/signup: Create a new access token
Full API documentation is available at: /api/v1/docs
```


**Note**: New users have only 1 hour to use their token before it expires.

## Improvements
Save user passwords securely, such as by using Supabase for user information storage.
Implement a rate limit for all users, with only 10 attempts allowed for freemium access.
