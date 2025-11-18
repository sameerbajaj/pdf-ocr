# PDF OCR Tool

Convert scanned or poorly OCR'd PDFs into searchable PDFs with selectable text using Tesseract OCR.

## Features

- 🎯 High-quality OCR using Tesseract 5.x
- 📄 Creates searchable PDFs with invisible text layer
- 🎨 Interactive, user-friendly command-line interface
- ⚡ Fast processing with configurable DPI (default: 300)
- 🎭 Process entire PDFs or specific page ranges

## Prerequisites

Install system dependencies first:

**macOS:**
```bash
brew install tesseract poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

## Quick Start

### Option 1: Run Directly from GitHub (Easiest - No Installation!)

```bash
uvx --from git+https://github.com/sameerbajaj/pdf-ocr pdf-ocr
```

That's it! The tool will run directly without any installation.

### Option 2: Clone and Run Locally

```bash
# Clone the repository
git clone https://github.com/sameerbajaj/pdf-ocr.git
cd pdf-ocr

# Run directly
uvx --from . pdf-ocr
```

### Option 3: Install Permanently

```bash
# Clone and install
git clone https://github.com/sameerbajaj/pdf-ocr.git
cd pdf-ocr
uv pip install -e .
source .venv/bin/activate

# Run from anywhere
pdf-ocr
```

## Usage

### Interactive Mode (Recommended)

Simply run the command and follow the friendly prompts:

```bash
pdf-ocr
```

The tool will ask you:
1. **Which PDF file?** - You can type the path or drag & drop the file
2. **Which pages?** - Enter a range like `4-5`, a single page like `7`, or press Enter for all pages

### Command-Line Mode

```bash
# Process entire PDF
pdf-ocr document.pdf

# Process specific pages
pdf-ocr document.pdf --pages 4-5
pdf-ocr document.pdf -p 1-10

# Custom output
pdf-ocr document.pdf --output result.pdf

# Save text files too
pdf-ocr document.pdf --save-text

# Higher quality (slower)
pdf-ocr document.pdf --dpi 400
```

## Examples

```bash
# Process pages 4-5 of a book
pdf-ocr book.pdf --pages 4-5

# Process chapter (pages 20-40) with text export
pdf-ocr textbook.pdf -p 20-40 --save-text

# High-quality scan of a single page
pdf-ocr scan.pdf --pages 7 --dpi 600
```

## Output

The tool generates:
- **`filename_ocr.pdf`** or **`filename_pages4-5_ocr.pdf`** - Searchable PDF with text layer
- **`filename_pageX.txt`** (optional) - Plain text files if `--save-text` is used

All files are saved in the same directory as the input PDF.

## Troubleshooting

**Command not found:**
```bash
source .venv/bin/activate
```

**Tesseract not installed:**
```bash
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Linux
```

**Poppler not installed:**
```bash
brew install poppler  # macOS
sudo apt-get install poppler-utils  # Linux
```

## Development

```bash
# Setup for development
git clone https://github.com/yourusername/pdf-ocr-tool.git
cd pdf-ocr-tool
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run from source
python -m pdf_ocr_tool.cli
```

## Project Structure

```
pdf-ocr-tool/
├── pdf_ocr_tool/          # Main package
│   ├── cli.py            # Command-line interface
│   ├── ocr.py            # OCR processing
│   └── pdf_utils.py      # PDF generation
├── pyproject.toml        # Package configuration
├── setup.sh              # Auto-installer script
└── README.md             # This file
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [pdf2image](https://github.com/Belval/pdf2image)
- [Rich](https://github.com/Textualize/rich)
