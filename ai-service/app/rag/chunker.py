from typing import List, Dict, Any


class TextChunker:
    """
    Splits claim details and evidence text documents into chunks while preserving metadata across each chunk.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits a single document dictionary into a list of chunk dictionaries.
        Each chunk contains its text snippet and full inherited metadata.
        """
        content = document.get("content", "").strip()
        if not content:
            return []

        document_id = document.get("document_id", "unknown_doc")
        claim_id = document.get("claim_id", "")
        evidence_id = document.get("evidence_id", "")
        source_type = document.get("type", document.get("source_type", "text"))
        timestamp = document.get("timestamp", document.get("uploadedAt", ""))
        title = document.get("title", document.get("fileName", "Document"))
        author = document.get("author", document.get("customerName", "Unknown"))

        chunks = []
        start = 0
        chunk_index = 0
        content_len = len(content)

        while start < content_len:
            end = min(start + self.chunk_size, content_len)
            
            # If not at the end of the text, try to break on a sentence boundary or word boundary
            if end < content_len:
                # Look for sentence boundary
                boundary = content.rfind('. ', start, end)
                if boundary != -1 and boundary > start + (self.chunk_size // 2):
                    end = boundary + 1
                else:
                    # Look for word boundary
                    space_boundary = content.rfind(' ', start, end)
                    if space_boundary != -1 and space_boundary > start + (self.chunk_size // 2):
                        end = space_boundary

            chunk_text = content[start:end].strip()

            if chunk_text:
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                chunk_metadata = {
                    "document_id": document_id,
                    "claim_id": claim_id,
                    "evidence_id": evidence_id,
                    "source_type": source_type,
                    "timestamp": str(timestamp),
                    "title": title,
                    "author": author,
                    "chunk_index": chunk_index,
                    "char_offset": start
                }

                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })
                chunk_index += 1

            if end >= content_len:
                break

            # Move start forward with overlap
            step = end - start - self.chunk_overlap
            if step <= 0:
                step = max(1, self.chunk_size - self.chunk_overlap)
            start += step

        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Splits a list of document dictionaries into a flat list of chunk dictionaries.
        """
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
