from google import genai

API_KEY = "AQ.Ab8RN6KL-eQdPMn9U6x0v2LGvz1-ugmGnQMpYcDikGd0EubLSg"

print("[-] Initializing Gemini Client...")
try:
    client = genai.Client(api_key=API_KEY)
    print("[+] Client initialized successfully.")
    
    print("[-] Fetching available models...")
    models = client.models.list()
    for m in models:
        print(f"  -> {m.name}")
            
    print("\n[+] PASS: Diagnostic complete. API Key & Client are 100% operational!")
except Exception as e:
    print(f"[-] FAIL: Diagnostic Error -> {e}")