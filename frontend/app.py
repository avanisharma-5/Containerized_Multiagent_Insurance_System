from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Light Theme Configuration
# ─────────────────────────────────────────────────────────────────────────────

def configure_light_theme() -> None:
    """Configure Streamlit with attractive white and light blue theme."""
    light_theme_css = """
    <style>
    /* Main theme colors */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
        color: #1e293b;
    }
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 600;
    }
    
    .stTitle {
        color: #0f172a !important;
        font-weight: 700;
    }
    
    .stCaption {
        color: #64748b !important;
        font-weight: 500;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    .css-1d391kg * {
        color: #1e293b;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #ffffff;
        color: #1e293b;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        padding: 2rem;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #1e293b;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
        color: #1e293b;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Select boxes */
    .stSelectbox > div > div > select {
        background-color: #ffffff;
        color: #1e293b;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        padding: 20px 40px;
        font-weight: 600;
        font-size: 16px;
        min-height: 56px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(59, 130, 246, 0.4);
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fed7aa;
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Error messages */
    .stError {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #1e293b;
        border: none;
        border-radius: 0;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 8px 16px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: transparent;
        color: #3b82f6;
        border: none;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Columns */
    .stColumns {
        background-color: #ffffff;
    }
    
    /* Metrics */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #ffffff;
        color: #1e293b;
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 24px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #3b82f6;
        background-color: #f8fafc;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 4px;
    }
    
    /* Spinner */
    .stSpinner {
        color: #3b82f6;
    }
    
    /* Dataframe */
    .dataframe {
        background-color: #ffffff;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
        color: #1e293b;
        font-weight: 600;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .dataframe td {
        background-color: #ffffff;
        color: #1e293b;
        border-bottom: 1px solid #f1f5f9;
        padding: 12px;
    }
    
    /* Code blocks */
    .code-block {
        background-color: #f8fafc;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Divider */
    .stDivider {
        border-color: #e2e8f0;
        border-width: 2px;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: #1e293b;
        font-weight: 500;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #1e293b;
        font-weight: 500;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 4px;
    }
    
    /* Markdown content */
    .stMarkdown {
        color: #1e293b;
    }
    
    /* Links */
    .stMarkdown a {
        color: #3b82f6;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }
    
    .stMarkdown a:hover {
        color: #2563eb;
        text-decoration: underline;
    }
    
    /* JSON output */
    .stJson {
        background-color: #f8fafc;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Captions */
    .stCaption {
        color: #64748b !important;
        font-style: italic;
    }
    
    /* Subheaders */
    .stSubheader {
        color: #1e293b !important;
        font-weight: 600;
    }
    </style>
    """
    st.markdown(light_theme_css, unsafe_allow_html=True)


DEFAULT_API_BASE = "http://127.0.0.1:8000"


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def api_url(base_url: str, path: str) -> str:
    normalized = base_url.strip().rstrip("/") + "/"
    return urljoin(normalized, path.lstrip("/"))


def init_state() -> None:
    st.session_state.setdefault("last_response", None)
    st.session_state.setdefault("comparison_result", None)


# ─────────────────────────────────────────────────────────────────────────────
# API calls
# ─────────────────────────────────────────────────────────────────────────────

def run_workflow(
    base_url: str,
    question: str,
    generate_image: bool,
    uploaded_pdf: Any | None,
) -> dict[str, Any]:
    data = {
        "question": question,
        "generate_image": generate_image,
    }
    files = None
    if uploaded_pdf is not None:
        files = {
            "file": (
                uploaded_pdf.name,
                uploaded_pdf.getvalue(),
                "application/pdf",
            )
        }
    response = requests.post(
        api_url(base_url, "/workflow/run-inline"),
        data=data,
        files=files,
        timeout=300,
    )
    response.raise_for_status()
    return response.json()


def run_comparison(
    base_url: str,
    pdf_a: Any,
    pdf_b: Any,
) -> dict[str, Any]:
    """POST both PDFs to /comparison/run and return the JSON response."""
    files = {
        "pdf_a": (pdf_a.name, pdf_a.getvalue(), "application/pdf"),
        "pdf_b": (pdf_b.name, pdf_b.getvalue(), "application/pdf"),
    }
    response = requests.post(
        api_url(base_url, "/comparison/run"),
        files=files,
        timeout=600,
    )
    if not response.ok:
        # Extract the real error detail from FastAPI's JSON error body
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise requests.HTTPError(
            f"HTTP {response.status_code}: {detail}",
            response=response,
        )
    return response.json()


# ─────────────────────────────────────────────────────────────────────────────
# Chat tab
# ─────────────────────────────────────────────────────────────────────────────

def render_chat_tab(base_url: str) -> None:
    st.markdown("### Chat Interface")
    
    # Input section
    upload = st.file_uploader("Upload PDF (optional)", type=["pdf"], key="chat_pdf")
    if upload is not None:
        st.success(f"Selected PDF: {upload.name}")
    else:
        st.info("No PDF uploaded. Responses will be general guidance.")

    question = st.text_area(
        "Question",
        placeholder="Ask insurance-related questions…",
        key="chat_question",
    )
    
    # Image generation code kept but UI removed
    generate_image = False  # Default to False, not shown in UI

    # Send button with increased padding
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Send", use_container_width=True, key="chat_send"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Running agents…"):
                    try:
                        result = run_workflow(
                            base_url=base_url,
                            question=question.strip(),
                            generate_image=generate_image,
                            uploaded_pdf=upload,
                        )
                        st.session_state.last_response = result
                    except requests.RequestException as exc:
                        st.error(f"Workflow failed: {exc}")
    
    st.divider()
    
    # Response section below send button
    st.subheader("Response")
    result = st.session_state.last_response
    if not result:
        st.info("No response yet.")
        return

    final_output = result.get("state", {}).get("final_output")
    if final_output:
        # Enhanced formatting for better structure
        if "##" in final_output or "**" in final_output:
            st.markdown(final_output)
        else:
            # Format plain text with better structure
            lines = final_output.split('\n')
            formatted_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    # Add formatting for key points
                    if any(keyword in line.lower() for keyword in ['important:', 'key:', 'note:', 'summary:']):
                        formatted_lines.append(f"**{line}**")
                    elif len(line) < 100 and line.endswith(':'):
                        formatted_lines.append(f"### {line}")
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append("")  # Preserve paragraph breaks
            
            formatted_text = '\n'.join(formatted_lines)
            st.markdown(formatted_text)
    else:
        st.json(result)

    image_url = result.get("image_url")
    if image_url:
        st.image(api_url(base_url, image_url), caption="Generated insurance image")


# ─────────────────────────────────────────────────────────────────────────────
# Comparison tab
# ─────────────────────────────────────────────────────────────────────────────

def _metric_row(label: str, val_a: str, val_b: str, highlight: str | None = None) -> None:
    """Render one row of the comparison table with optional winner highlight."""
    cols = st.columns([2, 1.5, 1.5])
    cols[0].markdown(f"**{label}**")
    # Highlight the winning cell in green
    if highlight == "a":
        cols[1].markdown(f":green[{val_a}]")
        cols[2].write(val_b)
    elif highlight == "b":
        cols[1].write(val_a)
        cols[2].markdown(f":green[{val_b}]")
    else:
        cols[1].write(val_a)
        cols[2].write(val_b)


def render_comparison_tab(base_url: str) -> None:
    st.markdown(
        "Upload **two** insurance policy PDFs. "
        "The agents will extract policy details and provide a focused comparison with key differences and suggestions."
    )

    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        pdf_a = st.file_uploader("Policy A (PDF)", type=["pdf"], key="cmp_pdf_a")
        if pdf_a:
            st.caption(f"✓ {pdf_a.name}  ·  {len(pdf_a.getvalue()) // 1024} KB")
    with col_b:
        pdf_b = st.file_uploader("Policy B (PDF)", type=["pdf"], key="cmp_pdf_b")
        if pdf_b:
            st.caption(f"✓ {pdf_b.name}  ·  {len(pdf_b.getvalue()) // 1024} KB")

    ready = pdf_a is not None and pdf_b is not None

    if st.button(
        "Compare policies →",
        use_container_width=True,
        disabled=not ready,
        key="cmp_run",
    ):
        with st.spinner("Analyzing policies and generating comparison report…"):
            try:
                result = run_comparison(base_url, pdf_a, pdf_b)
                st.session_state.comparison_result = result
            except requests.RequestException as exc:
                st.error(f"Comparison failed: {exc}")

    # ── Results ────────────────────────────────────────────────────────────────
    result = st.session_state.comparison_result
    if not result:
        if not ready:
            st.info("Upload both PDFs above to enable comparison.")
        return

    st.success("Comparison complete!")
    st.divider()

    # Display the comparison report
    report = result.get("report", "")
    if report:
        st.subheader("Policy Comparison Report")
        st.markdown(report)
    
    

    # ── Reset ──────────────────────────────────────────────────────────────────
    if st.button("Clear & compare again", key="cmp_reset"):
        st.session_state.comparison_result = None
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(page_title="Insurance Multi-Agent Assistant", layout="wide")
    
    # Apply attractive light theme
    configure_light_theme()
    
    st.title("Multi-Agent Insurance Assistant")
    st.caption("Chat · Document RAG · Policy Comparison")

    init_state()

    # Use default backend URL without sidebar input 
    base_url = DEFAULT_API_BASE

    chat_tab, compare_tab = st.tabs(["Chat", "Compare policies"])

    with chat_tab:
        render_chat_tab(base_url)

    with compare_tab:
        render_comparison_tab(base_url)


if __name__ == "__main__":
    main()