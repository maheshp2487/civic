import argparse
import json
import os
from app.rag.ingestion.models import DocumentMetadata, LegalChunk
from app.rag.ingestion.parser import LegalDocumentParser
from app.rag.ingestion.chunker import LegalAwareChunker
from app.rag.ingestion.embedder import GeminiEmbedder
from app.rag.ingestion.db import SupabaseIngestionDB

def process_file(file_path: str, metadata_dict: dict):
    print(f"Processing: {file_path}")
    
    metadata = DocumentMetadata(**metadata_dict)
    
    # 1. Parse Document
    print("  -> Extracting text...")
    text = LegalDocumentParser.extract_text(file_path)
    
    # 2. Chunk Text
    print("  -> Chunking document (Legal-Aware)...")
    chunk_metadatas = LegalAwareChunker.chunk_text(text)
    print(f"  -> Generated {len(chunk_metadatas)} chunks.")
    
    # 3. Embed
    print("  -> Generating Embeddings (gemini-embedding-2)...")
    embedder = GeminiEmbedder()
    legal_chunks = []
    
    for i, c_meta in enumerate(chunk_metadatas):
        embedding = embedder.embed_text(c_meta.chunk_text)
        legal_chunks.append(LegalChunk(metadata=c_meta, embedding=embedding))
        if (i+1) % 10 == 0:
            print(f"     Embedded {i+1}/{len(chunk_metadatas)} chunks...")
            
    # 4. Insert into Supabase
    print("  -> Inserting into Supabase...")
    db = SupabaseIngestionDB()
    
    try:
        source_id = db.insert_document(metadata, legal_chunks)
        print(f"[SUCCESS] Ingested document '{metadata.title}' with ID: {source_id}")
    except ValueError as e:
        print(f"[SKIPPED] {str(e)}")
    except Exception as e:
        print(f"[ERROR] Failed to insert: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Legal Document Ingestion Pipeline")
    parser.add_argument("--config", required=True, help="Path to JSON config defining documents to ingest.")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    for doc_config in config.get("documents", []):
        file_path = doc_config.get("file_path")
        metadata = doc_config.get("metadata")
        if not file_path or not metadata:
            print("Invalid configuration entry. Missing file_path or metadata.")
            continue
            
        try:
            process_file(file_path, metadata)
        except Exception as e:
            print(f"CRITICAL FAILURE processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()
