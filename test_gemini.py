import os
import streamlit as st
from google import genai

API_KEY = None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found.")
    st.stop()

API_KEY = API_KEY.strip()

client = genai.Client(api_key=API_KEY)