<h1 align="center">✨ AI Text Transformer</h1>

Deployment Link: https://ai-text-transformer-lk1612mt2qwu5bo22nfsf.streamlit.app/ 

A sleek Streamlit web app that rewrites and summarizes text using Google Gemini API.
Easily transform your text into different styles, summarize long passages, and export results with one click.
Features

Rewrite Text — transform text into different tones/styles.

Summarization — generate concise summaries (short / medium / long).

Document Upload — import text from PDF & DOCX files.

Clean UI/UX — modern, minimal layout with dark theme support.

Copy & Download — instantly copy output or export to .txt.

Privacy-Friendly — no data is stored, everything runs via secure API.

 Installation

Clone the repository

git clone https://github.com/your-username/ai-text-transformer.git
cd ai-text-transformer


Create virtual environment & install dependencies

pip install -r requirements.txt


Run the app locally

streamlit run app.py

API Key Setup

This project uses Google Gemini API.

Get your key from Google AI Studio
.

On Streamlit Cloud:

Open Settings → Secrets

Add:

GOOGLE_API_KEY="your_api_key_here"


Locally, you can also create a .env file (if not deploying):

GOOGLE_API_KEY=your_api_key_here

❤️
