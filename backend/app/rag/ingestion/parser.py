import os
import fitz  # PyMuPDF
from docx import Document

class LegalDocumentParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return LegalDocumentParser._extract_pdf(file_path)
        elif ext == ".docx":
            return LegalDocumentParser._extract_docx(file_path)
        elif ext in [".txt", ".md"]:
            return LegalDocumentParser._extract_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        text = ""
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Including a special marker for page numbers to preserve them for chunking
                text += f"\n---PAGE_{page_num+1}---\n"
                text += page.get_text("text")
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF {file_path}: {str(e)}")
        
        if not text.strip():
            raise ValueError("Extracted PDF text is empty.")
        return text

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        text = ""
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            raise RuntimeError(f"Failed to parse DOCX {file_path}: {str(e)}")
            
        if not text.strip():
            raise ValueError("Extracted DOCX text is empty.")
        return text

    @staticmethod
    def _extract_text_file(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            raise ValueError("Extracted Text file is empty.")
        return text
