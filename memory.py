"""Módulo de memória persistente para Jarvis.

Fornece uma interface unificada para armazenar e recuperar mensagens de conversa.  
Se `chromadb` estiver instalado, utiliza um banco vetorial persistente para recuperar recordações relevantes.  
Caso contrário, recorre a uma memória simples baseada em lista.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import numpy as np

from . import config

try:
    import chromadb  # type: ignore
    from chromadb.utils import embedding_functions  # type: ignore
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import openai  # type: ignore
except ImportError:
    openai = None  # type: ignore


@dataclass
class Message:
    role: str  # 'user' ou 'assistant'
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)


class SimpleMemory:
    """Fallback de memória baseado em lista.

    Mantém apenas as últimas `max_messages` interações no arquivo JSON.
    """

    def __init__(self, path: str, max_messages: int = 10) -> None:
        self.path = path
        self.max_messages = max_messages
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.messages: List[Message] = [Message(**msg) for msg in data]
            except Exception:
                self.messages = []
        else:
            self.messages = []

    def _save(self) -> None:
        data = [msg.__dict__ for msg in self.messages]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, message: Message) -> None:
        self.messages.append(message)
        # limitar o tamanho
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]
        self._save()

    def retrieve(self, query: str, k: int) -> List[Message]:
        """Retorna as últimas `k` mensagens simples para contexto."""
        return self.messages[-k:]


class VectorMemory:
    """Memória baseada em embeddings e banco vetorial.

    Usa o ChromaDB para armazenar mensagens e recuperá‑las por similaridade de texto.
    """

    def __init__(self, path: str, k: int = 3) -> None:
        if not CHROMADB_AVAILABLE:
            raise RuntimeError(
                "chromadb não está instalado. Use SimpleMemory ou instale chromadb."
            )
        self.path = path
        self.k = k
        # Criar diretório se não existir
        os.makedirs(path, exist_ok=True)
        # Inicializar cliente
        self.client = chromadb.PersistentClient(path=path)
        # Nomear coleção
        self.collection = self.client.get_or_create_collection(
            name="jarvis_memories"
        )
        # Definir função de embedding.  Usaremos a API da OpenAI se disponível.
        self.embedder = None
        if openai is not None and config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
            self.embedder = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-3-small"
            )
        else:
            # fallback para SentenceTransformer.  Requer sentence-transformers instalado.
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                model = SentenceTransformer("all-MiniLM-L6-v2")
                self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model
                )
            except Exception as e:
                raise RuntimeError(
                    "Nenhum gerador de embeddings disponível. Instale sentence-transformers ou configure OpenAI."
                )

    def add(self, message: Message) -> None:
        content = message.content
        # ID único: use timestamp e comprimento atual
        uid = f"{message.role}-{len(self.collection.get(ids=[]).ids) + 1}"
        meta = {"role": message.role, **message.metadata}
        self.collection.add(ids=[uid], documents=[content], metadatas=[meta])

    def retrieve(self, query: str, k: Optional[int] = None) -> List[Message]:
        k = k or self.k
        if not query.strip():
            return []
        # Consultar banco
        results = self.collection.query(
            query_texts=[query], n_results=k
        )
        messages = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            messages.append(Message(role=meta.get("role", "assistant"), content=doc, metadata=meta))
        return messages


def get_memory() -> object:
    """Retorna uma instância de memória apropriada com base na disponibilidade do Chromadb."""
    if CHROMADB_AVAILABLE:
        try:
            return VectorMemory(path=config.VECTOR_DB_PATH, k=config.RETRIEVE_K)
        except Exception:
            pass
    # fallback simples
    return SimpleMemory(path=config.SIMPLE_MEMORY_PATH, max_messages=config.SIMPLE_MEMORY_MAX)