from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(BASE_DIR / ".env"))


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str
    serpapi_api_key: str
    embedding_model: str
    chroma_dir: str
    uploads_dir: str
    chats_dir: str
    rag_min_chars: int
    hf_api_token: str
    hf_image_model: str


def load_settings() -> Settings:
    groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not groq_api_key:
        raise RuntimeError("Missing GROQ_API_KEY in backend/.env")

    return Settings(
        groq_api_key=groq_api_key,
        groq_model="groq/llama-3.1-8b-instant",
        serpapi_api_key=os.environ.get("SERPAPI_API_KEY", "").strip(),
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        chroma_dir="vector_store",
        uploads_dir="uploads",
        chats_dir="data/chats",
        rag_min_chars=250,
        hf_api_token=os.environ.get("HF_API_TOKEN", "").strip(),
        hf_image_model="stabilityai/stable-diffusion-xl-base-1.0"
    
    )
