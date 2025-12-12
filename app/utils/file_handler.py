import os
import uuid
from fastapi import UploadFile, HTTPException, status
from typing import Optional

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class FileHandler:
    """Utility for handling file uploads"""
    
    @staticmethod
    def validate_pdf(file: UploadFile) -> bool:
        """Validate that the file is a PDF"""
        if not file.filename:
            return False
        return file.filename.lower().endswith('.pdf')
    
    @staticmethod
    async def save_file(file: UploadFile) -> str:
        """Save uploaded file and return the URL"""
        # Validate file type
        if not FileHandler.validate_pdf(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos PDF são permitidos"
            )
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar arquivo: {str(e)}"
            )
        
        # Return relative URL
        return f"/uploads/{unique_filename}"
    
    @staticmethod
    def delete_file(file_url: Optional[str]) -> bool:
        """Delete a file given its URL"""
        if not file_url or not file_url.startswith("/uploads/"):
            return False
        
        filename = os.path.basename(file_url)
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
