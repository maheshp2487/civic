import pytest
from app.rag.ingestion.parser import LegalDocumentParser
from app.rag.ingestion.chunker import LegalAwareChunker
from app.rag.ingestion.models import DocumentMetadata, ChunkMetadata

def test_chunker_legal_boundaries():
    text = """---PAGE_1---
THE MODEL TENANCY ACT, 2021
CHAPTER I
PRELIMINARY
Section 1: Short title, extent and commencement.
(1) This Act may be called the Model Tenancy Act, 2021.
(2) It shall extend to the whole of the State.
Section 2: Definitions.
In this Act, unless the context otherwise requires,-
(a) "agreement" means the written agreement...
---PAGE_2---
CHAPTER II
TENANCY
Section 3: Tenancy Agreement.
No person shall, after the commencement of this Act, let or take on rent any premises except by an agreement in writing.
"""
    
    chunks = LegalAwareChunker.chunk_text(text)
    
    assert len(chunks) == 6
    
    assert chunks[0].section == "General"
    assert chunks[1].section == "CHAPTER I"
    assert chunks[2].section == "Section 1: Short title, extent and commencement."
    assert chunks[3].section == "Section 2: Definitions."
    assert chunks[4].section == "CHAPTER II"
    assert chunks[5].section == "Section 3: Tenancy Agreement."

def test_extract_text_empty_file(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("")
    
    with pytest.raises(ValueError, match="empty"):
        LegalDocumentParser._extract_text_file(str(p))

def test_metadata_validation():
    # Valid metadata
    meta = DocumentMetadata(
        title="Model Tenancy Act",
        type="act",
        authority="Ministry of Housing and Urban Affairs",
        jurisdiction={"country": "India"}
    )
    assert meta.type == "act"
    
    # Invalid type
    with pytest.raises(ValueError):
        DocumentMetadata(title="Invalid", type="unsupported_type")

