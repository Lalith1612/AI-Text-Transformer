from __future__ import annotations

import os
import streamlit as st
import google.generativeai as genai
from typing import Optional

# Prompt templates
REWRITE_PROMPT = """You are an expert writing assistant.
Rewrite the TEXT below in a {style} style.
Preserve meaning, improve clarity, and keep formatting (lists, newlines) when helpful.
Avoid adding facts not present in the original. Return only the rewritten text.

STYLE: {style}
TEXT:
{text}
"""

SUMMARIZE_PROMPT = """You are an expert writing assistant.
Summarize the TEXT below into a concise {length} summary. Preserve key facts and don't invent new information.
Return only the summary text.

TEXT:
{text}
"""

def _get_google_api_key() -> Optional[str]:
    """Fetch Google API key from Streamlit secrets or environment."""
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY")


def _build_model(model_name: str = "gemini-1.5-flash"):
    api_key = _get_google_api_key()
    if not api_key:
        raise ValueError("Google API key not found. Set GOOGLE_API_KEY in .streamlit/secrets.toml or as an environment variable.")
    genai.configure(api_key=api_key)
    # Use the convenience wrapper that worked previously in this project
    return genai.GenerativeModel(model_name)


def transform_text(style: str, text: str, custom_prompt: Optional[str] = None) -> str:
    """Rewrite `text` into the requested `style`. If `custom_prompt` is provided it will be used instead of the built-in template."""
    model = _build_model()
    prompt = custom_prompt if custom_prompt else REWRITE_PROMPT.format(style=style, text=text)
    # Use the model to generate content
    resp = model.generate_content(prompt)
    # The returned object usually has `.text` — guard for alternatives
    out = ""
    if hasattr(resp, "text"):
        out = resp.text
    elif isinstance(resp, dict):
        # try common nested fields
        out = resp.get("content") or resp.get("output") or str(resp)
    else:
        out = str(resp)
    return out.strip()


def summarize_text(text: str, length: str = "short") -> str:
    """Produce a short/medium/long summary of the input text."""
    model = _build_model()
    prompt = SUMMARIZE_PROMPT.format(length=length, text=text)
    resp = model.generate_content(prompt)
    if hasattr(resp, "text"):
        out = resp.text
    elif isinstance(resp, dict):
        out = resp.get("content") or resp.get("output") or str(resp)
    else:
        out = str(resp)
    return out.strip()
