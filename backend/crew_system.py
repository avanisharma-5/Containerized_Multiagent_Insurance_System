from __future__ import annotations



import json

import re

from pathlib import Path

from typing import List, Tuple



import requests



from .chat_store import load_history

from .config import BASE_DIR, load_settings

from .crew_setup import build_insurance_crew

from .rag import retrieve_evidence, retrieve_evidence_from_pdf_bytes

from .web_search import search_web





def _groq_model_id(groq_model: str) -> str:

    if "/" in groq_model:

        return groq_model.split("/", 1)[1]

    return groq_model





def groq_chat(messages: List[dict], temperature: float = 0.1) -> str:

    settings = load_settings()

    model_id = _groq_model_id(settings.groq_model)

    resp = requests.post(

        "https://api.groq.com/openai/v1/chat/completions",

        headers={

            "Authorization": f"Bearer {settings.groq_api_key}",

            "Content-Type": "application/json",

        },

        json={"model": model_id, "messages": messages, "temperature": temperature},

        timeout=60,

    )

    resp.raise_for_status()

    return resp.json()["choices"][0]["message"]["content"]





def classify_insurance_intent(question: str) -> Tuple[bool, str]:

    prompt = (

        "Classify if the user query is insurance-related.\n"

        "Return strict JSON only:\n"

        '{ "is_insurance_related": true|false, "reason": "..." }'

    )

    response = groq_chat(

        [{"role": "system", "content": prompt}, {"role": "user", "content": question}],

        temperature=0.0,

    )

    try:

        data = json.loads(response)

        if data.get("is_insurance_related") is True:

            return True, ""

        return False, data.get("reason") or "Not insurance-related."

    except Exception:

        return True, ""





def _resolve_pdf_paths(file_ids: List[str]) -> List[str]:

    settings = load_settings()

    uploads_dir = (BASE_DIR / settings.uploads_dir).resolve()

    paths: List[str] = []

    for fid in file_ids:

        matches = list(uploads_dir.glob(f"{fid}__*"))

        if not matches:

            continue

        file_path = matches[0]

        if file_path.suffix.lower() == ".pdf":

            paths.append(str(file_path))

    return paths





def _clean_answer_text(answer: str, source: str) -> str:

    cleaned = answer or ""

    # Remove inline citation tags like [file.pdf | page 15] or [page 15].

    cleaned = re.sub(r"\[[^\]]*\|\s*page\s*\d+[^\]]*\]", "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\[\s*page\s*\d+\s*\]", "", cleaned, flags=re.IGNORECASE)

    # Remove evidence preface blocks if model echoes them.

    cleaned = re.sub(r"(?is)evidence context:\s*.*?(?=(direct answer:|answer:|major types:|$))", "", cleaned)



    lower = cleaned.lower()

    markers = [m for m in ["direct answer:", "answer:"] if m in lower]

    if markers:

        idx = min(lower.index(m) for m in markers)

        cleaned = cleaned[idx:].strip()

    else:

        cleaned = cleaned.strip()



    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    if source == "PDF_RAG":

        prefix = "Based on the data provided:\n\n"

        if not cleaned.lower().startswith("based on the data provided"):

            cleaned = prefix + cleaned

    return cleaned





def run_insurance_agents(

    question: str,

    session_id: str,

    file_ids: List[str],

    inline_pdf: tuple[str, bytes] | None = None,

) -> str:

    is_related, reason = classify_insurance_intent(question)

    if not is_related:

        return (

            "I can help with insurance questions (coverage, premiums, deductibles, "

            "life/health/auto/property policies).\n\n"

            f"Your query does not seem insurance-related. Reason: {reason}\n\n"

            "Please rephrase with insurance details, and I will help."

        )



    if inline_pdf is not None:

        pdf_name, pdf_content = inline_pdf

        found, evidence = retrieve_evidence_from_pdf_bytes(

            question, filename=pdf_name, content=pdf_content, k=5

        )

    else:

        pdf_paths = _resolve_pdf_paths(file_ids)

        found, evidence = retrieve_evidence(question, pdf_paths=pdf_paths, k=5)

    source = "PDF_RAG"

    if not found:

        web = search_web(question, num_results=5)

        evidence = web

        source = "WEB_SERPAPI"



    if not evidence:

        fallback_prompt = (

            "You are an insurance assistant. No grounded document/web evidence is available.\n"

            "Provide a helpful general answer, clearly labeled as general guidance.\n"

            "Keep it concise and practical, and include what user details are needed for a precise answer."

        )

        try:

            return groq_chat(

                [

                    {"role": "system", "content": fallback_prompt},

                    {"role": "user", "content": question},

                ],

                temperature=0.2,

            )

        except Exception:

            return (

                "I could not find grounded insurance information in uploaded documents or web search.\n\n"

                "Please share policy type, region, and your specific concern."

            )



    # Use a direct grounded synthesis step so the final answer always sees evidence context.

    grounding_prompt = (

        "You are an insurance assistant.\n"

        "Use evidence to answer. Be concise and helpful.\n"

        "If PDF_RAG: use document excerpts.\n"

        "If WEB_SERPAPI: use web search results.\n"

        "Format: Clear headings, bullet points, practical advice.\n"

        "If insufficient info: state limitation clearly.\n"

        "Answer directly, no citations."

    )

    evidence_text = "\n\n".join(evidence[:3])  # Reduce evidence to top 3 to save tokens

    try:

        raw = groq_chat(

            [

                {"role": "system", "content": grounding_prompt},

                {

                    "role": "user",

                    "content": (

                        f"Question:\n{question}\n\n"

                        f"Source:\n{source}\n\n"

                        f"Evidence:\n{evidence_text}"

                    ),

                },

            ],

            temperature=0.2,

        )

        return _clean_answer_text(raw, source=source)

    except Exception:

        pass



    chat_history = load_history(session_id)

    recent = chat_history[-6:] if chat_history else []

    history_text = "\n".join([f'{m["role"]}: {m["content"]}' for m in recent]) or "No prior history."

    evidence_seed = f"SOURCE={source}\n" + "\n".join(evidence[:5])



    crew = build_insurance_crew(evidence_seed=evidence_seed)

    result = crew.kickoff(

        inputs={

            "question": question,

            "chat_history": history_text,

        }

    )

    return str(result)

