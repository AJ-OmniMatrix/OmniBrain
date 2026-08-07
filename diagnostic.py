import google.generativeai as genai

# Your actual key
genai.configure(api_key="AQ.Ab8RN6KtmdwWS1lFHXaESxwbbVuZz6JxmeN7nyVkmsJNAOK28Q")

print("Fetching available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)