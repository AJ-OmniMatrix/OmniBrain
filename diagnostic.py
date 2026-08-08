import os
import sys

print("--- OmniBrain Diagnostic Tool ---")
print(f"Python Version: {sys.version}")

try:
    import streamlit
    print("[+] Streamlit installed.")
except ImportError:
    print("[-] Streamlit missing.")

try:
    from google import genai
    print("[+] google-genai installed.")
except ImportError:
    print("[-] google-genai missing.")

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    print(f"[+] GEMINI_API_KEY found (starts with: {api_key[:6]}...)")
else:
    print("[-] GEMINI_API_KEY environment variable is NOT set.")