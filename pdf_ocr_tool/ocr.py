"""Core OCR processing functionality."""

import os
from pathlib import Path
from typing import List, Tuple
from PIL import Image
import pytesseract
from pdf2image import convert_from_path


class OCRProcessor:
    """Handle OCR processing for PDF pages."""
    
    def __init__(self, dpi: int = 300, tesseract_config: str = '--oem 3 --psm 3'):
        """
        Initialize OCR processor.
        
        Args:
            dpi: Resolution for PDF to image conversion (default: 300)
            tesseract_config: Tesseract configuration string
        """
        self.dpi = dpi
        self.tesseract_config = tesseract_config
    
    def check_dependencies(self) -> Tuple[bool, str]:
        """
        Check if required system dependencies are installed.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check Tesseract
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            return False, (
                "Tesseract OCR is not installed or not in PATH.\n"
                "Install it with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)"
            )
        
        # Check poppler (required by pdf2image)
        try:
            # This will fail if poppler is not installed
            from pdf2image.exceptions import PDFInfoNotInstalledError
            # Try a simple conversion to check if poppler works
            # We'll catch the error if it's not installed
        except ImportError:
            pass
        
        return True, "All dependencies are installed."
    
    def convert_pdf_to_images(
        self, 
        pdf_path: str, 
        page_range: Tuple[int, int] = None
    ) -> List[Image.Image]:
        """
        Convert PDF pages to images.
        
        Args:
            pdf_path: Path to PDF file
            page_range: Tuple of (start_page, end_page) or None for all pages
        
        Returns:
            List of PIL Image objects
        """
        kwargs = {'dpi': self.dpi}
        
        if page_range:
            kwargs['first_page'] = page_range[0]
            kwargs['last_page'] = page_range[1]
        
        try:
            images = convert_from_path(pdf_path, **kwargs)
            return images
        except Exception as e:
            if "poppler" in str(e).lower() or "pdftoppm" in str(e).lower():
                raise RuntimeError(
                    "Poppler is not installed or not in PATH.\n"
                    "Install it with: brew install poppler (macOS) or apt-get install poppler-utils (Linux)"
                )
            raise
    
    def ocr_image(self, image: Image.Image) -> str:
        """
        Perform OCR on a single image.
        
        Args:
            image: PIL Image object
        
        Returns:
            Extracted text as string
        """
        return pytesseract.image_to_string(image, config=self.tesseract_config)
    
    def ocr_image_to_pdf(self, image: Image.Image) -> bytes:
        """
        Perform OCR on image and return PDF bytes with text layer.
        
        Args:
            image: PIL Image object
        
        Returns:
            PDF bytes with searchable text layer
        """
        return pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
    
    def process_pdf(
        self,
        pdf_path: str,
        page_range: Tuple[int, int] = None,
        progress_callback=None
    ) -> List[Tuple[Image.Image, str]]:
        """
        Process PDF and return images with OCR text.
        
        Args:
            pdf_path: Path to PDF file
            page_range: Tuple of (start_page, end_page) or None for all pages
            progress_callback: Optional callback function for progress updates
        
        Returns:
            List of tuples (image, ocr_text)
        """
        images = self.convert_pdf_to_images(pdf_path, page_range)
        results = []
        
        for idx, image in enumerate(images):
            if progress_callback:
                progress_callback(idx + 1, len(images))
            
            ocr_text = self.ocr_image(image)
            results.append((image, ocr_text))
        
        return results
