from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import BASE_DIR, load_settings


GENERIC_INSURANCE_TERMS = {
    "insurance",
    "policy",
    "coverage",
    "premium",
    "claim",
    "health",
    "benefit",
    "insured",
    "deductible",
}


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]{3,}", text.lower())


def _vector_store_path(source_key: str) -> Path:
    settings = load_settings()
    root = (BASE_DIR / settings.chroma_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root / source_key


def _source_key(pdf_paths: List[str]) -> str:
    names = [Path(p).stem.replace(" ", "_") for p in sorted(pdf_paths)]
    return "__".join(names)[:180] or "default"


def _build_or_load_db(pdf_paths: List[str]) -> Chroma:
    settings = load_settings()
    store_path = _vector_store_path(_source_key(pdf_paths))
    embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    if store_path.exists() and any(store_path.iterdir()):
        return Chroma(
            persist_directory=str(store_path),
            embedding_function=embedding,
        )

    docs = []
    for pdf_path in pdf_paths:
        loader = PyPDFLoader(pdf_path)
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    return Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=str(store_path),
    )


def retrieve_evidence(query: str, pdf_paths: List[str], k: int = 5) -> Tuple[bool, List[str]]:
    settings = load_settings()
    if not pdf_paths:
        return False, []

    vector_db = _build_or_load_db(pdf_paths)
    docs_with_scores = vector_db.similarity_search_with_score(query, k=k)
    if not docs_with_scores:
        return False, []

    top_score = docs_with_scores[0][1]
    contexts: List[str] = []
    total_chars = 0
    context_text_parts: List[str] = []
    for doc, _score in docs_with_scores:
        text = doc.page_content.strip()
        if len(text) < 40:
            continue
        metadata = doc.metadata or {}
        page = metadata.get("page", "unknown")
        if isinstance(page, int):
            page = page + 1
        source_name = Path(str(metadata.get("source", ""))).name or "document"
        contexts.append(f"[{source_name} | page {page}] {text}")
        context_text_parts.append(text)
        total_chars += len(text)

    found_by_length = total_chars >= settings.rag_min_chars
    try:
        # Chroma distance values vary by embedding/model; avoid brittle tiny thresholds.
        found_by_score = top_score is not None and float(top_score) <= 2.0
    except Exception:
        found_by_score = False

    query_tokens = set(_tokens(query))
    context_tokens = set(_tokens(" ".join(context_text_parts)))
    overlap = len(query_tokens.intersection(context_tokens))
    found_by_overlap = overlap / max(1, len(query_tokens)) >= 0.2

    specific_query_tokens = {t for t in query_tokens if t not in GENERIC_INSURANCE_TERMS}
    specific_hits = True if not specific_query_tokens else any(t in context_tokens for t in specific_query_tokens)

    has_context = len(contexts) > 0
    # Consider evidence grounded when we actually retrieved substantial chunks and
    # they pass at least one relevance signal, while still enforcing specific token checks.
    is_grounded = has_context and specific_hits and (found_by_score or found_by_overlap or found_by_length)
    return is_grounded, contexts


def retrieve_evidence_from_pdf_bytes(
    query: str, filename: str, content: bytes, k: int = 3  # Reduce k to save tokens
) -> Tuple[bool, List[str]]:
    settings = load_settings()
    if not content:
        return False, []

    suffix = Path(filename or "upload.pdf").suffix or ".pdf"
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            temp_path = tmp.name

        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        if not docs:
            return False, []

        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=150)  # Reduce chunk size
        splits = splitter.split_documents(docs)
        if not splits:
            return False, []

        for chunk in splits:
            chunk.metadata = chunk.metadata or {}
            chunk.metadata["source"] = filename or "uploaded.pdf"

        embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        vector_db = Chroma.from_documents(documents=splits, embedding=embedding)
        docs_with_scores = vector_db.similarity_search_with_score(query, k=k)
        if not docs_with_scores:
            return False, []

        top_score = docs_with_scores[0][1]
        contexts: List[str] = []
        total_chars = 0
        context_text_parts: List[str] = []
        for doc, _score in docs_with_scores:
            text = doc.page_content.strip()
            if len(text) < 40:
                continue
            metadata = doc.metadata or {}
            page = metadata.get("page", "unknown")
            if isinstance(page, int):
                page = page + 1
            source_name = Path(str(metadata.get("source", ""))).name or "document"
            contexts.append(f"[{source_name} | page {page}] {text}")
            context_text_parts.append(text)
            total_chars += len(text)

        found_by_length = total_chars >= settings.rag_min_chars
        try:
            found_by_score = top_score is not None and float(top_score) <= 2.0
        except Exception:
            found_by_score = False

        query_tokens = set(_tokens(query))
        context_tokens = set(_tokens(" ".join(context_text_parts)))
        overlap = len(query_tokens.intersection(context_tokens))
        found_by_overlap = overlap / max(1, len(query_tokens)) >= 0.2

        specific_query_tokens = {t for t in query_tokens if t not in GENERIC_INSURANCE_TERMS}
        specific_hits = True if not specific_query_tokens else any(
            t in context_tokens for t in specific_query_tokens
        )
        has_context = len(contexts) > 0
        is_grounded = has_context and specific_hits and (
            found_by_score or found_by_overlap or found_by_length
        )
        return is_grounded, contexts
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
