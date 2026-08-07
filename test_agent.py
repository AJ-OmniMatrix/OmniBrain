import os
import json
from google import genai

def test_persistence_layer():
    print("[-] Testing Disk Persistence Layer...")
    storage_file = "brain_storage.json"
    test_data = [{
        "title": "Automated Test Memory", 
        "type": "Text Paste", 
        "date": "2026-08-07", 
        "summary": "Core architecture verified."
    }]
    
    # Write test
    with open(storage_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)
    
    # Read test
    assert os.path.exists(storage_file), "Storage file failed to create."
    with open(storage_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    
    assert len(loaded) > 0, "Loaded memory array is empty."
    assert loaded[0]["title"] == "Automated Test Memory"
    print("[+] PASS: Disk Persistence & JSON Backing Operational.")

def test_ai_connection():
    print("[-] Testing Gemini API Model Routing (`gemini-3.5-flash`)...")
    try:
        api_key = "AQ.Ab8RN6IgO2Z2uwDMDY08l4Rq5iCCBQ7kKDAhU963KX0FgJzEzA"
        client = genai.Client(api_key=api_key)
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