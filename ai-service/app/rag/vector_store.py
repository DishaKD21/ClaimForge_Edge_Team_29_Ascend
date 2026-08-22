import os
import sqlite3
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger("VectorStore")


class VectorStore:
    """
    Persistent Local Vector Database using ChromaDB and Sentence Transformers.
    Features an offline TF-IDF fallback for keyless/lightweight test execution.
    Supports similarity search filtered by claim_id and source_type.
    """
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        model_name: str = "all-MiniLM-L6-v2",
        collection_name: str = "claim_chunks"
    ):
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.collection_name = collection_name
        self.backend_type = "chroma"  # "chroma" or "tfidf_fallback"

        self.chroma_client = None
        self.collection = None
        self.embedding_model = None

        self._init_backend()

    def _init_backend(self):
        """Attempts to initialize ChromaDB & SentenceTransformers, falling back to TF-IDF if needed."""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            os.makedirs(self.persist_directory, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            self.embedding_model = SentenceTransformer(self.model_name)
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
            self.backend_type = "chroma"
            logger.info(f"Initialized ChromaDB with SentenceTransformer('{self.model_name}') at {self.persist_directory}")
        except Exception as e:
            logger.warning(f"ChromaDB/SentenceTransformers initialization skipped: {e}. Activating persistent TF-IDF fallback.")
            self.backend_type = "tfidf_fallback"
            self._init_tfidf_fallback()

    def _init_tfidf_fallback(self):
        """Initializes local SQLite-backed store for TF-IDF fallback vectors."""
        os.makedirs(self.persist_directory, exist_ok=True)
        self.fallback_db_path = os.path.join(self.persist_directory, "fallback_vector_store.db")
        with sqlite3.connect(self.fallback_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    claim_id TEXT,
                    source_type TEXT,
                    metadata_json TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Embeds and stores chunks in the persistent vector database.
        Returns the number of added chunks.
        """
        if not chunks:
            return 0

        if self.backend_type == "chroma":
            return self._add_chunks_chroma(chunks)
        else:
            return self._add_chunks_tfidf(chunks)

    def _add_chunks_chroma(self, chunks: List[Dict[str, Any]]) -> int:
        ids = []
        documents = []
        metadatas = []
        texts_to_embed = []
        for c in chunks:
            chunk_id = c["chunk_id"]
            text = c["text"]
            meta = c.get("metadata", {})

            # Clean metadata values to ensure primitive types for ChromaDB
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(clean_meta)
            texts_to_embed.append(text)

        embeddings = self.embedding_model.encode(texts_to_embed).tolist()

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(chunks)

    def _add_chunks_tfidf(self, chunks: List[Dict[str, Any]]) -> int:
        """Stores chunks into local SQLite fallback database."""
        with sqlite3.connect(self.fallback_db_path) as conn:
            for c in chunks:
                chunk_id = c["chunk_id"]
                text = c["text"]
                meta = c.get("metadata", {})
                claim_id = meta.get("claim_id", "")
                source_type = meta.get("source_type", "")
                meta_json = json.dumps(meta)

                conn.execute(
                    "INSERT OR REPLACE INTO chunks (chunk_id, text, claim_id, source_type, metadata_json) VALUES (?, ?, ?, ?, ?)",
                    (chunk_id, text, claim_id, source_type, meta_json)
                )
            conn.commit()
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        claim_id: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search over chunked documents.
        Supports metadata filtering by claim_id and source_type.
        Returns a list of dicts with: chunk_id, text, metadata, similarity_score.
        """
        if self.backend_type == "chroma":
            return self._search_chroma(query, top_k, claim_id, source_type)
        else:
            return self._search_tfidf(query, top_k, claim_id, source_type)

    def _search_chroma(
        self,
        query: str,
        top_k: int = 5,
        claim_id: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Build metadata filter query
        where_filter = {}
        conditions = []
        if claim_id:
            conditions.append({"claim_id": claim_id})
        if source_type:
            conditions.append({"source_type": source_type})

        if len(conditions) == 1:
            where_filter = conditions[0]
        elif len(conditions) > 1:
            where_filter = {"$and": conditions}

        query_embedding = self.embedding_model.encode([query]).tolist()

        kwargs = {
            "query_embeddings": query_embedding,
            "n_results": top_k
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)

        search_results = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results.get("distances", [[]])[0]

            for i in range(len(ids)):
                dist = distances[i] if i < len(distances) else 0.0
                # Convert distance to similarity score (e.g. 1 / (1 + distance))
                similarity_score = round(float(1.0 / (1.0 + max(0, dist))), 4)

                search_results.append({
                    "chunk_id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i],
                    "similarity_score": similarity_score
                })

        return search_results

    def _search_tfidf(
        self,
        query: str,
        top_k: int = 5,
        claim_id: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback TF-IDF similarity search over SQLite database."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            # Fallback string matching if scikit-learn is not installed
            return self._search_simple_keyword(query, top_k, claim_id, source_type)

        sql = "SELECT chunk_id, text, claim_id, source_type, metadata_json FROM chunks"
        params = []
        where_clauses = []
        if claim_id:
            where_clauses.append("claim_id = ?")
            params.append(claim_id)
        if source_type:
            where_clauses.append("source_type = ?")
            params.append(source_type)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        with sqlite3.connect(self.fallback_db_path) as conn:
            rows = conn.execute(sql, params).fetchall()

        if not rows:
            return []

        chunk_ids = [r[0] for r in rows]
        texts = [r[1] for r in rows]
        metadatas = [json.loads(r[4]) for r in rows]

        try:
            vectorizer = TfidfVectorizer().fit(texts + [query])
            text_vectors = vectorizer.transform(texts)
            query_vector = vectorizer.transform([query])

            similarities = cosine_similarity(query_vector, text_vectors)[0]
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = round(float(similarities[idx]), 4)
                results.append({
                    "chunk_id": chunk_ids[idx],
                    "text": texts[idx],
                    "metadata": metadatas[idx],
                    "similarity_score": score
                })
            return results
        except Exception as e:
            logger.error(f"TF-IDF fallback search failed: {e}")
            return self._search_simple_keyword(query, top_k, claim_id, source_type)

    def _search_simple_keyword(
        self,
        query: str,
        top_k: int = 5,
        claim_id: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        sql = "SELECT chunk_id, text, claim_id, source_type, metadata_json FROM chunks"
        params = []
        where_clauses = []
        if claim_id:
            where_clauses.append("claim_id = ?")
            params.append(claim_id)
        if source_type:
            where_clauses.append("source_type = ?")
            params.append(source_type)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        with sqlite3.connect(self.fallback_db_path) as conn:
            rows = conn.execute(sql, params).fetchall()

        query_words = set(query.lower().split())
        results = []
        for r in rows:
            chunk_id, text, _, _, meta_json = r
            text_words = set(text.lower().split())
            intersection = query_words.intersection(text_words)
            score = round(len(intersection) / max(1, len(query_words)), 4)
            results.append({
                "chunk_id": chunk_id,
                "text": text,
                "metadata": json.loads(meta_json),
                "similarity_score": score
            })
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def reset(self):
        """Clears all indexed vectors from database."""
        if self.backend_type == "chroma" and self.collection:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        elif hasattr(self, 'fallback_db_path'):
            with sqlite3.connect(self.fallback_db_path) as conn:
                conn.execute("DELETE FROM chunks")
                conn.commit()
