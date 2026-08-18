from app.core.database import get_supabase_client
from app.rag.ingestion.models import DocumentMetadata, LegalChunk
from typing import List

class SupabaseIngestionDB:
    def __init__(self):
        self.client = get_supabase_client()

    def document_exists(self, title: str, source_url: str) -> bool:
        """Check if a document already exists to ensure idempotency."""
        try:
            res = self.client.table("legal_sources").select("id").eq("title", title).execute()
            if res.data:
                return True
            if source_url:
                res_url = self.client.table("legal_sources").select("id").eq("source_url", source_url).execute()
                if res_url.data:
                    return True
            return False
        except Exception as e:
            raise RuntimeError(f"Database query failed during idempotency check: {str(e)}")

    def insert_document(self, metadata: DocumentMetadata, chunks: List[LegalChunk]) -> str:
        if self.document_exists(metadata.title, metadata.source_url or ""):
            raise ValueError(f"Document '{metadata.title}' already exists in the database. Skipping.")

        try:
            # Prepare source data
            source_data = metadata.model_dump(mode="json", exclude_none=True)
            
            # Insert legal_source
            source_res = self.client.table("legal_sources").insert(source_data).execute()
            if not source_res.data:
                raise RuntimeError("Failed to insert legal source, no data returned.")
            source_id = source_res.data[0]["id"]
            
            # Prepare chunks
            chunk_data_list = []
            for chunk in chunks:
                chunk_data_list.append({
                    "source_id": source_id,
                    "chunk_text": chunk.metadata.chunk_text,
                    "page_number": chunk.metadata.page_number,
                    "section": chunk.metadata.section,
                    "embedding": chunk.embedding
                })
            
            # Insert legal_chunks in batches of 100
            batch_size = 100
            for i in range(0, len(chunk_data_list), batch_size):
                batch = chunk_data_list[i:i+batch_size]
                self.client.table("legal_chunks").insert(batch).execute()
                
            return source_id
        except Exception as e:
            raise RuntimeError(f"Database insertion failed: {str(e)}")
