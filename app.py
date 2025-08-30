import streamlit as st
import traceback
import json
from utils.document_parser import parse_document
from chains import text_chains
import io

# --- Page Config ---
st.set_page_config(
    page_title="AI Text Transformer",
    page_icon="✨",
    layout="wide",
)

# --- Custom CSS (dark theme only) ---
def _local_css():
    css = """
    <style>
    :root { --bg: #0f1114; --card: #121217; --muted: #9aa0a6; --accent: #646cff; --text: #e6eef8; }
    .stApp { background-color: var(--bg); color: var(--text); }
    .title { text-align: center; font-size: 2.4rem; font-weight: 700; margin-bottom: 0.25rem; color: var(--text); }
    .subtitle { text-align: center; color: var(--muted); margin-bottom: 1.5rem; }
    .box { background: var(--card); padding: 1rem; border-radius: 10px; border: 1px solid #222; }
    .output-box { background: #0b0c0f; color: var(--text); padding: 1rem; border-radius: 8px; border: 1px solid #222; white-space: pre-wrap; min-height: 200px; }
    .muted { color: var(--muted); font-size: 0.9rem; }
    .controls { display:flex; gap:8px; }
    button.copy-btn { background: var(--accent); color: white; padding: 8px 12px; border: none; border-radius:6px; cursor:pointer; }
    a.link { color: var(--accent); }
    .small { font-size: 0.9rem; color: var(--muted); }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

_local_css()

# --- Header ---
st.markdown('<div class="title">✨ AI Text Transformer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Rewrite, summarize and export text using a generative model. Fast, simple and privacy-friendly.</div>', unsafe_allow_html=True)

# --- Sidebar configuration ---
with st.sidebar:
    st.header("⚙️ Options")
    mode = st.selectbox("Mode", ["Rewrite", "Summarize"], index=0)

    if mode == "Rewrite":
        st.markdown("**Choose style(s)** (you can pick multiple)")
        styles = st.multiselect(
            "Styles", 
            ["Formal", "Casual", "Professional", "Poetic", "Simplified"], 
            default=["Formal"]
        )
        st.markdown("**Or provide a custom style/prompt**")
        custom_style = st.text_area(
            "Custom style / instruction", 
            height=80, 
            placeholder="E.g. Write like a technical blog, or 'Explain like I'm 5'"
        )
    else:
        styles = []
        custom_style = None

    st.markdown("---")
    summarize_length = st.selectbox("Summary length", ["short","medium","long"], index=0)
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload (PDF or DOCX) to prefill input", type=["pdf","docx"])

# --- Session state ---
if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_input" not in st.session_state:
    st.session_state["last_input"] = ""

# --- Layout ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(" Input Text")
    text_input = st.text_area("Enter your text here:", height=250, value=st.session_state["last_input"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        file_stream = io.BytesIO(file_bytes)
        text_input = parse_document(file_stream, uploaded_file.type)
    except Exception as e:
        st.error(f"Error parsing document: {e}")

    # Word/char count
    if text_input.strip():
        st.markdown(f"<div class='small'>Words: {len(text_input.split())} • Characters: {len(text_input)}</div>", unsafe_allow_html=True)

# Actions row (equal sized buttons)
cols = st.columns(3)
transform_btn = cols[0].button("✨ Transform", use_container_width=True)
clear_btn = cols[1].button("✖ Clear Input", use_container_width=True)
undo_btn = cols[2].button("↺ Restore Last Input", use_container_width=True)

with col2:
    st.subheader(" Output")
    # text_input = st.textbox("Your transformed text is here:", height=250, value=st.session_state["last_input"])
    output_container = st.container()

    if st.session_state["history"]:
        last = st.session_state["history"][-1]
        # Renders all outputs from last run
        for o in last["outputs"]:
            st.markdown(
                f"<div class='output-box' id='out-{o['id']}'>{o['text']}</div>",
                unsafe_allow_html=True
            )
            js = f"""
            <button class='copy-btn' onclick='navigator.clipboard.writeText({json.dumps(o['text'])})'>Copy</button>
            """
            st.markdown(js, unsafe_allow_html=True)
            st.download_button("Download .txt", o['text'], file_name=f"output_{o['style']}.txt")
    else:
        st.markdown(
            "<div class='output-box muted'>Your output will appear here after transformation.</div>",
            unsafe_allow_html=True
        )

# --- Button logic ---
if transform_btn and text_input.strip():
    try:
        outputs = []
        if mode == "Rewrite":
            if custom_style:
                out = text_chains.transform_text(custom_style, text_input, custom_prompt=None)
                outputs.append({"id":"custom","style":"Custom","text":out})
            for style in styles:
                out = text_chains.transform_text(style, text_input)
                outputs.append({"id":style.lower(),"style":style,"text":out})
        else:  # Summarize
            out = text_chains.summarize_text(text_input, length=summarize_length)
            outputs.append({"id":"summary","style":f"Summary-{summarize_length}","text":out})

        st.session_state["history"].append({"input": text_input, "outputs": outputs})
        st.session_state["last_input"] = text_input
        st.rerun()
    except Exception as e:
        st.error(f"Transformation error: {e}")
        st.code(traceback.format_exc())

if clear_btn:
    st.session_state["last_input"] = ""
    st.rerun()

if undo_btn and len(st.session_state["history"]) > 1:
    st.session_state["history"].pop()
    st.session_state["last_input"] = st.session_state["history"][-1]["input"]
    st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("**About**")
st.markdown("AI Text Transformer — rewrite and summarize text using a generative model. Built for demos and quick editing.")
st.markdown("**Tips:** Use the sidebar to switch mode and styles. Use 'Custom style' for any special instructions.")

st.markdown("---")

st.markdown('<div class="subtitle">Made with ❤️ — Powered by Google Gemini.</div>', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center;'>"
    "<a href='https://github.com/your-username/your-repo' target='_blank'>Project Repo</a> • "
    "<a href='docs.pdf' target='_blank'>Docs</a>"
    "</div>",
    unsafe_allow_html=True
)

