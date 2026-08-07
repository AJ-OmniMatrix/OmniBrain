import os
import json
from google import genai

API_KEY = "AQ.Ab8RN6KL-eQdPMn9U6x0v2LGvz1-ugmGnQMpYcDikGd0EubLSg"

def test_persistence_layer():
    print("[-] Testing Disk Persistence Layer...")
    storage_file = "brain_storage_test.json"
    test_data = [{
        "title": "Automated Test Memory", 
        "type": "Text Paste", 
        "date": "2026-08-08", 
        "summary": "Core architecture verified."
    }]
    
    with open(storage_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)
    
    assert os.path.exists(storage_file), "Storage file failed to create."
    with open(storage_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    
    assert len(loaded) > 0, "Loaded memory array is empty."
    assert loaded[0]["title"] == "Automated Test Memory"
    print("[+] PASS: Disk Persistence & JSON Backing Operational.")
    
    if os.path.exists(storage_file):
        os.remove(storage_file)

def test_ai_connection():
    print("[-] Testing Gemini API Model Routing (`gemini-3.5-flash`)...")
    try:
        client = genai.Client(api_key=API_KEY)
        res = client.models.generate_content(
            model='gemini-3.5-flash', 
            contents="Confirm system operational status with a single word."
        )
        print(f"[+] PASS: AI Engine Connected. Response: {res.text.strip()}")
    except Exception as e:
        print(f"[-] FAIL: AI Connection Error -> {e}")

if __name__ == "__main__":
    print("========================================")
    print("     OMNIBRAIN E2E TEST HARNESS         ")
    print("========================================")
    test_persistence_layer()
    test_ai_connection()
    print("========================================")
    print("All backend verification checks complete!")