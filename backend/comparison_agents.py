from __future__ import annotations

"""
comparison_agents.py  (Windows-compatible, robust chart path handling)
"""

import base64
import json
import os
import re
import tempfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_groq import ChatGroq


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _groq_llm() -> ChatGroq:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    model = os.environ.get("GROQ_MODEL", "groq/llama-3.1-8b-instant")
    return ChatGroq(model=model, temperature=0.1, api_key=api_key)


def _extract_json_block(text: str) -> dict:
    """Pull first JSON object from a possibly markdown-wrapped string."""
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON object found in:\n{text[:400]}")


def _normalize_number(value: Any) -> float:
    """'$1,200' / '85%' / 1200 → float. Returns 0.0 on failure."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[^0-9.]", "", value)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def _validate_extraction(pdf_text: str, extracted_data: dict) -> dict:
    """Validate that extracted data actually exists in PDF text."""
    policy_data = extracted_data.copy()
    pdf_text_lower = pdf_text.lower()
    
    # Check if premium information exists in text
    premium_keywords = ['premium', 'annual premium', 'yearly premium', 'cost', 'price']
    has_premium = any(keyword in pdf_text_lower for keyword in premium_keywords)
    if not has_premium:
        policy_data['premium'] = 0
    
    # Check if coverage information exists in text
    coverage_keywords = ['coverage', 'coverage amount', 'insured amount', 'limit', 'benefit']
    has_coverage = any(keyword in pdf_text_lower for keyword in coverage_keywords)
    if not has_coverage:
        policy_data['coverage'] = 0
    
    # Check if claim ratio information exists in text
    claim_keywords = ['claim ratio', 'loss ratio', 'claims', 'ratio', 'percentage']
    has_claim_ratio = any(keyword in pdf_text_lower for keyword in claim_keywords)
    if not has_claim_ratio:
        policy_data['claim_ratio'] = 0
    
    return policy_data


def _windows_safe_tmp() -> str:
    """
    Return a writable temp directory that works on Windows.
    Uses TEMP/TMP env vars, falling back to the system tempdir.
    """
    for env in ("TEMP", "TMP"):
        val = os.environ.get(env, "").strip()
        if val and Path(val).is_dir():
            return val
    return tempfile.gettempdir()


def _pdf_text_simple(pdf_path: str, max_chars: int = 8000) -> str:
    try:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        combined = " ".join(p.page_content for p in pages)
        return combined[:max_chars]
    except Exception as exc:
        return f"[Could not read PDF: {exc}]"


def _enhance_extraction(pdf_text: str, extracted_data: dict) -> dict:
    """Enhance extraction by doing keyword matching on raw text."""
    enhanced_data = extracted_data.copy()
    text_lower = pdf_text.lower()
    
    # Premium variations
    premium_terms = ['premium', 'annual premium', 'yearly premium', 'cost', 'price', 'amount', 'fee', 'payment']
    if enhanced_data.get('premium') == 0 and any(term in text_lower for term in premium_terms):
        enhanced_data['premium'] = 'Found in text - needs manual extraction'
    
    # Coverage variations
    coverage_terms = ['coverage', 'sum insured', 'insured amount', 'limit', 'benefit', 'maximum coverage', 'coverage amount']
    if enhanced_data.get('sum_insured') == 0 and any(term in text_lower for term in coverage_terms):
        enhanced_data['sum_insured'] = 'Found in text - needs manual extraction'
    
    # Claim ratio variations
    claim_terms = ['claim settlement ratio', 'loss ratio', 'claims', 'settlement', 'ratio', 'claim ratio']
    if enhanced_data.get('claim_settlement_ratio') == 0 and any(term in text_lower for term in claim_terms):
        enhanced_data['claim_settlement_ratio'] = 'Found in text - needs manual extraction'
    
    return enhanced_data


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class PolicyComparisonPipeline:
    """
    Simple policy comparison: Analyzer → Writer
    """

    def __init__(self, output_dir: str = ""):
        self.output_dir = output_dir or _windows_safe_tmp()
        self.llm = _groq_llm()

    # ── Step 1: Analyzer ─────────────────────────────────────────────────────

    def _run_analyzer(self, pdf_path_a: str, pdf_path_b: str) -> dict:
        # Read PDFs directly in Python instead of using a tool
        text_a = _pdf_text_simple(pdf_path_a)
        text_b = _pdf_text_simple(pdf_path_b)
        
        # Debug: Print first 500 chars of each PDF to see what we're working with
        print(f"\nDEBUG - PDF A content preview: {text_a[:500]}")
        print(f"\nDEBUG - PDF B content preview: {text_b[:500]}")
        
        pdf_content = (
            f"=== POLICY A ({Path(pdf_path_a).name}) ===\n{text_a}\n\n"
            f"=== POLICY B ({Path(pdf_path_b).name}) ===\n{text_b}"
        )
        
        analyzer = Agent(
            role="Insurance Policy Analyzer",
            goal=(
                "Extract comprehensive policy details from two insurance PDFs and return "
                "a structured JSON with all key factors for comparison."
            ),
            backstory=(
                "A meticulous insurance analyst who reads policy documents and "
                "extracts all relevant coverage details, terms, and conditions."
            ),
            tools=[],  # No tools - data injected directly into prompt
            llm=self.llm,
            verbose=True,
        )

        analyze_task = Task(
            description=(
                f"Extract policy details from two PDFs:\n\n"
                f"PDF A: {Path(pdf_path_a).name}\n"
                f"PDF B: {Path(pdf_path_b).name}\n\n"
                f"Content A: {text_a[:4000]}\n\n"
                f"Content B: {text_b[:4000]}\n\n"
                "Extract: policy_name, coverage_type, sum_insured, premium, premium_frequency, claim_settlement_ratio, add_ons, waiting_periods, age_variations, income_variations, gender_variations, other_variations.\n\n"
                "Look for: premium, coverage, sum insured, claim settlement, add-on, waiting period, age, income, gender variations.\n\n"
                "Return JSON: {{\"policy_a\":{{policy_name,coverage_type,sum_insured,premium,premium_frequency,claim_settlement_ratio,add_ons,waiting_periods,age_variations,income_variations,gender_variations,other_variations}},\"policy_b\":{{same fields}}}}"
            ),
            expected_output="JSON with extracted policy details.",
            agent=analyzer,
        )

        crew = Crew(agents=[analyzer], tasks=[analyze_task],
                    process=Process.sequential, verbose=True)
        raw = str(crew.kickoff())

        try:
            raw_data = _extract_json_block(raw)
            
            # Enhance extraction with keyword matching
            enhanced_a = _enhance_extraction(text_a, raw_data.get("policy_a", {}))
            enhanced_b = _enhance_extraction(text_b, raw_data.get("policy_b", {}))
            
            return {
                "policy_a": enhanced_a,
                "policy_b": enhanced_b
            }
        except Exception:
            return {
                "policy_a": {
                    "policy_name": Path(pdf_path_a).stem,
                    "coverage_type": "Not found",
                    "sum_insured": 0,
                    "premium": 0,
                    "premium_frequency": "Not found",
                    "claim_settlement_ratio": 0,
                    "add_ons": [],
                    "waiting_periods": [],
                    "age_variations": "",
                    "income_variations": "",
                    "gender_variations": "",
                    "other_variations": ""
                },
                "policy_b": {
                    "policy_name": Path(pdf_path_b).stem,
                    "coverage_type": "Not found",
                    "sum_insured": 0,
                    "premium": 0,
                    "premium_frequency": "Not found",
                    "claim_settlement_ratio": 0,
                    "add_ons": [],
                    "waiting_periods": [],
                    "age_variations": "",
                    "income_variations": "",
                    "gender_variations": "",
                    "other_variations": ""
                }
            }

    # ── Step 2: Writer ────────────────────────────────────────────────────────

    def _run_writer(self, structured_data: dict) -> str:
        pol_a = structured_data["policy_a"]
        pol_b = structured_data["policy_b"]
        name_a = pol_a.get("policy_name", "Policy A")
        name_b = pol_b.get("policy_name", "Policy B")

        # Prepare context data directly instead of using a tool
        context_payload = json.dumps(structured_data, indent=2)

        writer_agent = Agent(
            role="Insurance Comparison Writer",
            goal="Compare two insurance policies and highlight key differences with practical suggestions.",
            backstory=(
                "An experienced insurance advisor who analyzes policy differences and provides "
                "clear, actionable recommendations based on coverage and terms."
            ),
            tools=[],  # No tools - data injected directly into prompt
            llm=self.llm,
            verbose=True,
        )

        write_task = Task(
            description=(
                f"Compare policies:\n\n"
                f"Policy A: {pol_a.get('policy_name', 'Policy A')}\n"
                f"Policy B: {pol_b.get('policy_name', 'Policy B')}\n\n"
                f"Data: {context_payload}\n\n"
                "Focus on differences. Format:\n\n"
                "## Key Differences\n### Coverage & Sum Insured\n### Premiums\n### Claim Settlement Ratio\n### Add-ons\n### Waiting Periods\n### Variations\n## Suggestions (2-3 practical tips)"
            ),
            expected_output="Clear comparison with differences and suggestions.",
            agent=writer_agent,
        )

        crew = Crew(agents=[writer_agent], tasks=[write_task],
                    process=Process.sequential, verbose=True)
        return str(crew.kickoff())

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self, pdf_path_a: str, pdf_path_b: str) -> "ComparisonResult":
        print(f"\n{'='*60}\nSTEP 1/2 – Analyzer\n{'='*60}")
        structured_data = self._run_analyzer(pdf_path_a, pdf_path_b)
        print(f"✅ Structured data:\n{json.dumps(structured_data, indent=2)}")

        print(f"\n{'='*60}\nSTEP 2/2 – Writer\n{'='*60}")
        report = self._run_writer(structured_data)
        print(f"✅ Report ({len(report)} chars)")

        return ComparisonResult(
            structured_data=structured_data,
            report=report,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Result container
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ComparisonResult:
    structured_data: dict
    report: str