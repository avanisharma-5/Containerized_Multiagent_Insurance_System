from __future__ import annotations

import base64
from pathlib import Path
from uuid import uuid4

import requests

from .config import BASE_DIR, load_settings


def generate_insurance_image(prompt: str) -> str:
    settings = load_settings()
    if not settings.hf_api_token:
        raise RuntimeError("HF_API_TOKEN missing in backend/.env for image generation.")

    styled_prompt = (
        "Insurance themed, clean professional flat illustration, minimal text, "
        f"topic: {prompt}"
    )
    url = f"https://api-inference.huggingface.co/models/{settings.hf_image_model}"
    headers = {"Authorization": f"Bearer {settings.hf_api_token}"}
    payload = {"inputs": styled_prompt}
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type:
        data = resp.json()
        raise RuntimeError(f"Image model response error: {data}")

    image_bytes = resp.content
    image_dir = (BASE_DIR / "data" / "generated_images").resolve()
    image_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4()}.png"
    path = image_dir / filename
    path.write_bytes(image_bytes)
    return f"/images/{filename}"


def image_to_base64(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")
