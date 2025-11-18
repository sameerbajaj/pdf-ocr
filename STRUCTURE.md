# Project Structure

This is a standard Python package structure optimized for easy distribution and use.

## Directory Layout

```
pdf-ocr-tool/
├── pdf_ocr_tool/           # Python package (required structure)
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── ocr.py              # OCR processing engine
│   └── pdf_utils.py        # PDF generation utilities
│
├── pyproject.toml          # Package metadata and dependencies
├── setup.sh                # Automated installer script
├── requirements.txt        # Dependencies for notebook
├── LICENSE                 # MIT License
├── README.md               # Main documentation
├── .gitignore              # Git ignore rules
│
├── pdf_ocr_notebook.ipynb  # Optional: Jupyter notebook for testing
└── .venv/                  # Virtual environment (auto-created)
```

## Why This Structure?

### The `pdf_ocr_tool/` folder is required
This is **not** an unnecessary subfolder - it's the standard Python package structure. When you install with `uv pip install -e .`, Python looks for this package directory.

### Files You Need:
- ✅ `pdf_ocr_tool/` - The actual Python package
- ✅ `pyproject.toml` - Tells Python how to install the package
- ✅ `README.md` - Documentation
- ✅ `LICENSE` - Legal terms
- ✅ `setup.sh` - Optional installer helper

### Files for Development:
- `pdf_ocr_notebook.ipynb` - For testing and experimentation
- `requirements.txt` - Notebook dependencies
- `.venv/` - Virtual environment (auto-created, not in git)

## How It Works

1. **User runs**: `uvx --from . pdf-ocr`
2. **uvx reads**: `pyproject.toml` to find the package
3. **Python finds**: `pdf_ocr_tool/` package directory
4. **Executes**: `pdf_ocr_tool/cli.py:main()` function
5. **User gets**: Interactive OCR tool

## Publishing to GitHub

When you publish this to GitHub, users can run:

```bash
uvx --from git+https://github.com/yourusername/pdf-ocr-tool pdf-ocr
```

The structure must stay as-is for this to work properly.
