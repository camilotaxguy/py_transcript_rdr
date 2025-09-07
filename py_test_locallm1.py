import requests
import json
#
# To test the LM Studio server
# using requests
#
# LM Studio server URL
url = "http://localhost:1234/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

data = {
    "model": "local-model",  # or your specific model name
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about AI."}
    ],
    "temperature": 0.7,
    "max_tokens": 200,
    "stream": False
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result['choices']['message']['content'])
else:
    print(f"Error: {response.status_code} - {response.text}")
