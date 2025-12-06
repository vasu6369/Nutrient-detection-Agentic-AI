# agent/tools/rag_tool.py
from __future__ import annotations

import os
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer, util


class RAGTool:
    """
    Very simple local RAG over .txt files in rag_folder.
    """

    def __init__(self, rag_folder: str = "rag_docs"):
        self.rag_folder = rag_folder
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.docs: List[str] = []
        self.embeddings = None

        self._load_docs()

    def _load_docs(self) -> None:
        if not os.path.exists(self.rag_folder):
            print(f"[RAG] Folder '{self.rag_folder}' not found. RAG disabled.")
            self.docs = []
            self.embeddings = None
            return

        all_texts: List[str] = []
        for file in os.listdir(self.rag_folder):
            if file.endswith(".txt"):
                path = os.path.join(self.rag_folder, file)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    self.docs.append(text)
                    all_texts.append(text)

        if not all_texts:
            print(f"[RAG] No .txt documents found in '{self.rag_folder}'.")
            self.embeddings = None
            return

        # Embed documents
        self.embeddings = self.model.encode(all_texts, convert_to_tensor=True)
        print(f"[RAG] Loaded {len(all_texts)} documents.")

    def search(self, query: str, top_k: int = 2) -> Dict[str, Any]:
        if not self.docs or self.embeddings is None:
            print("[RAG] No documents available; returning empty results.")
            return {"query": query, "results": []}

        query_embedding = self.model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, self.embeddings, top_k=top_k)[0]

        results: List[str] = []
        for h in hits:
            results.append(self.docs[h["corpus_id"]])

        print("RAG:", query, "->", len(results), "results")
        return {
            "query": query,
            "results": results,
        }
