import os
import magic
import pyclamd
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path
from datetime import datetime
import uuid
import redis

app = FastAPI()

# Security
security = HTTPBearer()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'application/pdf',
    'text/plain', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}
UPLOAD_DIR = "uploads"
TEMP_DIR = "temp_uploads"

# Setup
Path(UPLOAD_DIR).mkdir(exist_ok=True)
Path(TEMP_DIR).mkdir(exist_ok=True)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ClamAV
try:
    cd = pyclamd.ClamdUnixSocket()
    cd.ping()
except pyclamd.ConnectionError:
    raise Exception("Could not connect to ClamAV daemon")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, implement proper JWT validation
    token = credentials.credentials
    if not redis_client.exists(f"token:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return token

def scan_file(file_path: str) -> bool:
    try:
        scan_result = cd.scan_file(file_path)
        return scan_result is None  # None means no virus found
    except pyclamd.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Virus scanner unavailable"
        )

def validate_file(file: UploadFile):
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Check MIME type
    mime = magic.Magic(mime=True)
    file_content = file.file.read(1024)
    file.file.seek(0)
    mime_type = mime.from_buffer(file_content)
    
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {mime_type}"
        )

@app.post("/upload", status_code=201)
async def upload_files(
    files: List[UploadFile] = File(...),
    token: str = Depends(verify_token)
):
    results = []
    
    for file in files:
        try:
            validate_file(file)
            
            # Save to temp location for scanning
            temp_filename = f"{uuid.uuid4()}_{file.filename}"
            temp_path = os.path.join(TEMP_DIR, temp_filename)
            
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Scan for viruses
            if not scan_file(temp_path):
                os.remove(temp_path)
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"File {file.filename} contains malware"
                )
            
            # Move to permanent storage
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"{timestamp}_{file.filename}"
            final_path = os.path.join(UPLOAD_DIR, final_filename)
            os.rename(temp_path, final_path)
            
            results.append({
                "filename": file.filename,
                "saved_as": final_filename,
                "size": os.path.getsize(final_path),
                "status": "success"
            })
            
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "error": e.detail,
                "status": "failed"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e),
                "status": "failed"
            })
    
    return {"results": results}

@app.get("/files")
async def list_files(token: str = Depends(verify_token)):
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        files.append({
            "name": filename,
            "size": os.path.getsize(file_path),
            "modified": os.path.getmtime(file_path)
        })
    return {"files": files}