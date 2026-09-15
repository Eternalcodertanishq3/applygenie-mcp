"""Resume text extraction from PDF and DOCX files."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_text_from_pdf(filepath: str | Path) -> str:
    """Use pdfplumber if available, fallback to PyPDF2."""
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except ImportError:
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        except ImportError:
            return "Error: Please install pdfplumber or PyPDF2 (pip install pdfplumber PyPDF2)"

def extract_text_from_docx(filepath: str | Path) -> str:
    """Use python-docx."""
    try:
        import docx
        doc = docx.Document(filepath)
        return "\n".join(para.text for para in doc.paragraphs)
    except ImportError:
        return "Error: Please install python-docx (pip install python-docx)"

def extract_resume_text(filepath: str | Path) -> str:
    """Auto-detect format and extract."""
    path = Path(filepath)
    if not path.exists():
        return f"Error: File not found {filepath}"
        
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    elif ext == ".docx":
        return extract_text_from_docx(path)
    elif ext == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    else:
        return f"Error: Unsupported file format {ext}"
