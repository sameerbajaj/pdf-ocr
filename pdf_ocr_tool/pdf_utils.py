"""PDF generation utilities."""

import os
from pathlib import Path
from typing import List
from PIL import Image
import pytesseract


def create_searchable_pdf(
    images: List[Image.Image],
    output_path: str,
    progress_callback=None
) -> str:
    """
    Create a searchable PDF from images with OCR text layer.
    
    Args:
        images: List of PIL Image objects
        output_path: Path for output PDF file
        progress_callback: Optional callback for progress updates
    
    Returns:
        Path to created PDF file
    """
    try:
        # Use PyPDF2 to merge multiple pages
        from PyPDF2 import PdfMerger
    except ImportError:
        # Fallback: create single-page or multi-page PDF directly
        return _create_pdf_direct(images, output_path, progress_callback)
    
    merger = PdfMerger()
    temp_files = []
    
    try:
        for idx, image in enumerate(images):
            if progress_callback:
                progress_callback(idx + 1, len(images))
            
            # Create temporary PDF for each page
            temp_pdf = f".temp_page_{idx}_{os.getpid()}.pdf"
            temp_files.append(temp_pdf)
            
            # Generate searchable PDF using pytesseract
            pdf_data = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            
            with open(temp_pdf, 'wb') as f:
                f.write(pdf_data)
            
            merger.append(temp_pdf)
        
        # Write the merged PDF
        merger.write(output_path)
        merger.close()
        
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
    
    return output_path


def _create_pdf_direct(
    images: List[Image.Image],
    output_path: str,
    progress_callback=None
) -> str:
    """
    Create PDF directly when PyPDF2 is not available.
    
    For single page PDFs or fallback method.
    """
    if len(images) == 1:
        # Single page - direct conversion
        if progress_callback:
            progress_callback(1, 1)
        
        pdf_data = pytesseract.image_to_pdf_or_hocr(images[0], extension='pdf')
        with open(output_path, 'wb') as f:
            f.write(pdf_data)
    else:
        # Multiple pages - need to combine somehow
        # This is a fallback - try using img2pdf if available
        try:
            import img2pdf
            
            # Convert images to bytes
            image_bytes_list = []
            for idx, img in enumerate(images):
                if progress_callback:
                    progress_callback(idx + 1, len(images))
                
                # Create OCR PDF for this page
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                image_bytes_list.append(pdf_bytes)
            
            # For now, just save the first one with a warning
            with open(output_path, 'wb') as f:
                f.write(image_bytes_list[0])
            
            print("Warning: PyPDF2 not available. Only first page saved.")
            print("Install PyPDF2 for multi-page PDF support: uv pip install PyPDF2")
            
        except ImportError:
            # No merge capability - save first page only
            pdf_data = pytesseract.image_to_pdf_or_hocr(images[0], extension='pdf')
            with open(output_path, 'wb') as f:
                f.write(pdf_data)
            
            print("Warning: Limited PDF support. Only first page saved.")
            print("Install PyPDF2 for multi-page PDF support: uv pip install PyPDF2")
    
    return output_path


def save_text_files(
    ocr_results: List[tuple],
    output_dir: str,
    base_name: str,
    start_page: int = 1
) -> List[str]:
    """
    Save OCR text to individual text files.
    
    Args:
        ocr_results: List of (image, text) tuples
        output_dir: Directory to save text files
        base_name: Base name for output files
        start_page: Starting page number for naming
    
    Returns:
        List of created file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    
    for idx, (image, text) in enumerate(ocr_results):
        page_num = start_page + idx
        text_file = output_dir / f"{base_name}_page{page_num}.txt"
        
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        created_files.append(str(text_file))
    
    return created_files
