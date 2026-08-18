import re
from typing import List
from app.rag.ingestion.models import ChunkMetadata

class LegalAwareChunker:
    @staticmethod
    def chunk_text(text: str) -> List[ChunkMetadata]:
        lines = text.split('\n')
        chunks = []
        
        current_section = "General"
        current_page = 1
        current_chunk_lines = []
        
        # Matches: "Section 4.", "Section 4:", "Article 12", "Chapter V"
        boundary_pattern = re.compile(r"^(?:Section|Article|Chapter|Rule|Regulation)\s+[0-9A-Z]+[:.]?", re.IGNORECASE)
        page_pattern = re.compile(r"^---PAGE_(\d+)---$")
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            page_match = page_pattern.match(line_stripped)
            if page_match:
                current_page = int(page_match.group(1))
                continue
                
            if boundary_pattern.match(line_stripped):
                # Save previous chunk
                if current_chunk_lines:
                    chunks.append(ChunkMetadata(
                        chunk_text="\n".join(current_chunk_lines),
                        page_number=current_page,
                        section=current_section
                    ))
                    current_chunk_lines = []
                # Update current section. We take the first 100 chars max to avoid grabbing a whole paragraph if the regex matches loosely.
                current_section = line_stripped[:100]
                
            current_chunk_lines.append(line_stripped)
            
            # Safety fallback for extreme cases (e.g. 4000 characters without a legal boundary)
            if sum(len(l) for l in current_chunk_lines) > 4000:
                chunks.append(ChunkMetadata(
                    chunk_text="\n".join(current_chunk_lines),
                    page_number=current_page,
                    section=current_section + " (Continued)"
                ))
                current_chunk_lines = []
                
        # Append the final chunk
        if current_chunk_lines:
            chunks.append(ChunkMetadata(
                chunk_text="\n".join(current_chunk_lines),
                page_number=current_page,
                section=current_section
            ))
            
        return chunks
