import pytest
from io import BytesIO
from fastapi import UploadFile, HTTPException
from app.utils.file_handler import FileHandler


class TestFileHandler:
    """Test FileHandler utility"""
    
    def test_validate_pdf_valid(self):
        """Test validating a valid PDF file"""
        file = UploadFile(filename="test.pdf", file=BytesIO(b"test"))
        
        result = FileHandler.validate_pdf(file)
        
        assert result is True
    
    def test_validate_pdf_invalid_extension(self):
        """Test validating file with invalid extension"""
        file = UploadFile(filename="test.jpg", file=BytesIO(b"test"))
        
        result = FileHandler.validate_pdf(file)
        
        assert result is False
    
    def test_validate_pdf_no_filename(self):
        """Test validating file with no filename"""
        file = UploadFile(filename=None, file=BytesIO(b"test"))
        
        result = FileHandler.validate_pdf(file)
        
        assert result is False
    
    def test_validate_pdf_uppercase_extension(self):
        """Test validating PDF with uppercase extension"""
        file = UploadFile(filename="test.PDF", file=BytesIO(b"test"))
        
        result = FileHandler.validate_pdf(file)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_save_file_valid_pdf(self):
        """Test saving a valid PDF file"""
        content = b"%PDF-1.4 test content"
        file = UploadFile(filename="test.pdf", file=BytesIO(content))
        
        file_url = await FileHandler.save_file(file)
        
        assert file_url.startswith("/uploads/")
        assert file_url.endswith(".pdf")
        
        # Cleanup
        FileHandler.delete_file(file_url)
    
    @pytest.mark.asyncio
    async def test_save_file_invalid_type(self):
        """Test saving an invalid file type"""
        file = UploadFile(filename="test.jpg", file=BytesIO(b"test"))
        
        with pytest.raises(HTTPException) as exc_info:
            await FileHandler.save_file(file)
        
        assert exc_info.value.status_code == 400
        assert "PDF" in exc_info.value.detail
    
    def test_delete_file_valid_url(self):
        """Test deleting a file with valid URL"""
        # We'll test with a non-existent file, which should return False
        result = FileHandler.delete_file("/uploads/nonexistent.pdf")
        
        assert result is False
    
    def test_delete_file_invalid_url(self):
        """Test deleting file with invalid URL"""
        result = FileHandler.delete_file("/static/test.pdf")
        
        assert result is False
    
    def test_delete_file_none(self):
        """Test deleting file with None URL"""
        result = FileHandler.delete_file(None)
        
        assert result is False
