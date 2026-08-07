from google import genai

# Direct authentication with your key
API_KEY = "AQ.Ab8RN6IgO2Z2uwDMDY08l4Rq5iCCBQ7kKDAhU963KX0FgJzEzA"
client = genai.Client(api_key=API_KEY)

print("Fetching available models...")
try:
    for m in client.models.list():
        print(m.name)
    print("[+] PASS: Model listing successful.")
except Exception as e:
    print(f"[-] FAIL: Error fetching models -> {e}")