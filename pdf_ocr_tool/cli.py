"""Command-line interface for PDF OCR tool."""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Tuple

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from .ocr import OCRProcessor
from .pdf_utils import create_searchable_pdf, save_text_files


console = Console()


def parse_page_range(page_range_str: str) -> Tuple[int, int]:
    """
    Parse page range string like '4-5', '1-10', '5' into tuple.
    
    Args:
        page_range_str: String like "4-5" or "4" or "1-10"
    
    Returns:
        Tuple of (start_page, end_page)
    
    Raises:
        ValueError: If format is invalid
    """
    page_range_str = page_range_str.strip()
    
    if '-' in page_range_str:
        parts = page_range_str.split('-')
        if len(parts) != 2:
            raise ValueError("Invalid page range format. Use 'start-end' like '4-5' or '1-10'")
        
        try:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
        except ValueError:
            raise ValueError("Page numbers must be integers")
        
        if start < 1 or end < 1:
            raise ValueError("Page numbers must be positive (starting from 1)")
        
        if start > end:
            raise ValueError(f"Start page ({start}) must be less than or equal to end page ({end})")
        
        return (start, end)
    else:
        try:
            page = int(page_range_str)
        except ValueError:
            raise ValueError("Invalid page number. Must be an integer")
        
        if page < 1:
            raise ValueError("Page numbers must be positive (starting from 1)")
        
        return (page, page)


def normalize_path(path_str: str) -> Path:
    """
    Normalize file path, handling backslashes and spaces.
    
    Args:
        path_str: Input path string (may contain backslashes from copy-paste)
    
    Returns:
        Normalized Path object
    """
    # Remove backslashes used as escape characters (common when copy-pasting macOS paths)
    path_str = path_str.replace('\\ ', ' ')
    
    # Expand user home directory
    path_str = os.path.expanduser(path_str)
    
    # Convert to Path and resolve
    return Path(path_str).resolve()


def validate_pdf_path(pdf_path: Path) -> None:
    """
    Validate that PDF file exists and is readable.
    
    Args:
        pdf_path: Path to PDF file
    
    Raises:
        click.ClickException: If file is invalid
    """
    if not pdf_path.exists():
        raise click.ClickException(f"File not found: {pdf_path}")
    
    if not pdf_path.is_file():
        raise click.ClickException(f"Not a file: {pdf_path}")
    
    if pdf_path.suffix.lower() != '.pdf':
        console.print("[yellow]Warning: File doesn't have .pdf extension[/yellow]")
    
    if not os.access(pdf_path, os.R_OK):
        raise click.ClickException(f"File not readable: {pdf_path}")


@click.command()
@click.argument('pdf_path', type=str, required=False)
@click.option(
    '--pages', '-p',
    type=str,
    help='Page range to process (e.g., "4-5", "1-10", "7"). Leave empty for all pages.'
)
@click.option(
    '--output', '-o',
    type=str,
    help='Output PDF path (default: adds "_ocr" suffix to input filename)'
)
@click.option(
    '--dpi',
    type=int,
    default=300,
    help='DPI for image conversion (default: 300, higher = better quality but slower)'
)
@click.option(
    '--save-text/--no-save-text',
    default=False,
    help='Also save extracted text to .txt files'
)
@click.option(
    '--output-dir',
    type=str,
    help='Directory for output files (default: same as input PDF)'
)
@click.version_option(version="1.0.0", prog_name="pdf-ocr")
def main(
    pdf_path: Optional[str],
    pages: Optional[str],
    output: Optional[str],
    dpi: int,
    save_text: bool,
    output_dir: Optional[str]
):
    """
    High-quality OCR tool for scanned PDFs using Tesseract.
    
    Convert scanned PDFs into searchable PDFs with selectable text.
    
    Examples:
    
        # Interactive mode
        pdf-ocr
        
        # Process entire PDF
        pdf-ocr document.pdf
        
        # Process specific pages
        pdf-ocr document.pdf --pages 4-5
        pdf-ocr document.pdf -p 1-10
        
        # Process with custom output
        pdf-ocr document.pdf --output result.pdf
        
        # Process with text files
        pdf-ocr document.pdf --save-text
    """
    console.print(Panel.fit(
        "[bold cyan]PDF OCR Tool[/bold cyan]\n"
        "High-quality OCR for scanned PDFs",
        border_style="cyan"
    ))
    
    # Interactive mode if no PDF path provided
    if not pdf_path:
        console.print("\n[bold cyan]Step 1: Select your PDF file[/bold cyan]")
        console.print("  • You can type the full path to your PDF")
        console.print("  • Or drag and drop the PDF file into this terminal")
        console.print("  • Press Enter when done\n")
        pdf_path = input("📄 PDF file path: ").strip()
        
        if not pdf_path:
            console.print("[red]✗ No PDF path provided. Exiting.[/red]")
            sys.exit(1)
    
    # Normalize and validate PDF path
    try:
        pdf_path_obj = normalize_path(pdf_path)
        validate_pdf_path(pdf_path_obj)
    except click.ClickException as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)
    
    console.print(f"\n[green]✓[/green] Found PDF: [bold]{pdf_path_obj.name}[/bold]")
    
    # Interactive page range if not provided
    page_range = None
    if pages:
        try:
            page_range = parse_page_range(pages)
            console.print(f"[green]✓[/green] Processing pages: [bold]{page_range[0]}-{page_range[1]}[/bold]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    else:
        console.print("\n[bold cyan]Step 2: Choose which pages to process[/bold cyan]")
        console.print("  • Enter a page range like: [bold]4-5[/bold] (pages 4 through 5)")
        console.print("  • Or a single page like: [bold]7[/bold] (just page 7)")
        console.print("  • Or press [bold]Enter[/bold] to process the entire PDF\n")
        console.print("[dim]Examples: 4-5, 1-10, 20-25, or just 7[/dim]\n")
        pages_input = input("📖 Which pages? (press Enter for all): ").strip()
        
        if pages_input:
            try:
                page_range = parse_page_range(pages_input)
                console.print(f"\n[green]✓[/green] Will process pages: [bold]{page_range[0]} to {page_range[1]}[/bold]")
            except ValueError as e:
                console.print(f"[red]✗ Error: {e}[/red]")
                sys.exit(1)
        else:
            console.print("\n[green]✓[/green] Will process [bold]all pages[/bold] in the PDF")
    
    # Determine output directory
    if output_dir:
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = pdf_path_obj.parent
    
    # Determine output PDF path
    if output:
        output_pdf = normalize_path(output)
    else:
        # Generate output filename
        base_name = pdf_path_obj.stem
        if page_range:
            suffix = f"_pages{page_range[0]}-{page_range[1]}_ocr"
        else:
            suffix = "_ocr"
        output_pdf = out_dir / f"{base_name}{suffix}.pdf"
    
    console.print(f"[green]✓[/green] Output PDF: [bold]{output_pdf.name}[/bold]")
    
    # Initialize OCR processor
    processor = OCRProcessor(dpi=dpi)
    
    # Check dependencies
    console.print("\n[bold]Checking dependencies...[/bold]")
    success, message = processor.check_dependencies()
    if not success:
        console.print(f"[red]✗ {message}[/red]")
        sys.exit(1)
    console.print("[green]✓ All dependencies installed[/green]")
    
    # Process PDF
    console.print("\n[bold cyan]Starting OCR processing...[/bold cyan]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Convert PDF to images
            task1 = progress.add_task(
                f"[cyan]Converting PDF to images (DPI: {dpi})...",
                total=None
            )
            images = processor.convert_pdf_to_images(str(pdf_path_obj), page_range)
            progress.update(task1, completed=True)
            console.print(f"[green]✓[/green] Converted [bold]{len(images)}[/bold] page(s) to images")
            
            # Perform OCR
            task2 = progress.add_task(
                "[cyan]Performing OCR on pages...",
                total=len(images)
            )
            
            ocr_results = []
            for idx, image in enumerate(images):
                progress.update(task2, advance=1, description=f"[cyan]OCR on page {idx + 1}/{len(images)}...")
                ocr_text = processor.ocr_image(image)
                ocr_results.append((image, ocr_text))
            
            console.print(f"[green]✓[/green] OCR completed for [bold]{len(images)}[/bold] page(s)")
            
            # Create searchable PDF
            task3 = progress.add_task(
                "[cyan]Creating searchable PDF...",
                total=len(images)
            )
            
            def pdf_progress(current, total):
                progress.update(task3, completed=current)
            
            create_searchable_pdf(images, str(output_pdf), pdf_progress)
            console.print(f"[green]✓[/green] Created searchable PDF: [bold]{output_pdf}[/bold]")
            
            # Save text files if requested
            if save_text:
                task4 = progress.add_task("[cyan]Saving text files...", total=None)
                start_page = page_range[0] if page_range else 1
                text_files = save_text_files(
                    ocr_results,
                    str(out_dir),
                    pdf_path_obj.stem,
                    start_page
                )
                progress.update(task4, completed=True)
                console.print(f"[green]✓[/green] Saved [bold]{len(text_files)}[/bold] text file(s)")
        
        # Summary
        file_size = output_pdf.stat().st_size / (1024 * 1024)  # MB
        
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            f"[bold green]✓ OCR Complete![/bold green]\n\n"
            f"[bold]Output PDF:[/bold] {output_pdf}\n"
            f"[bold]File size:[/bold] {file_size:.2f} MB\n"
            f"[bold]Pages processed:[/bold] {len(images)}\n"
            f"[bold]Status:[/bold] Searchable & selectable text ✓",
            border_style="green",
            title="Success"
        ))
        
        # Show sample text
        if ocr_results:
            sample_text = ocr_results[0][1][:200].strip()
            if sample_text:
                console.print(f"\n[dim]Sample text from first page:[/dim]")
                console.print(f"[dim]{sample_text}...[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]✗ Error during processing:[/red]")
        console.print(f"[red]{str(e)}[/red]")
        
        if "poppler" in str(e).lower():
            console.print("\n[yellow]Install poppler with:[/yellow]")
            console.print("  macOS: [bold]brew install poppler[/bold]")
            console.print("  Linux: [bold]apt-get install poppler-utils[/bold]")
        
        sys.exit(1)


if __name__ == '__main__':
    main()
