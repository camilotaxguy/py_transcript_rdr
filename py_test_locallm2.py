import requests
import json

def test_lm_studio():
    # Test if server is running
    try:
        models_response = requests.get("http://localhost:1234/v1/models")
        if models_response.status_code == 200:
            print("✅ LM Studio server is running")
            models = models_response.json()
            print(f"Available models: {[model['id'] for model in models['data']]}")
        else:
            print("❌ LM Studio server not responding")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to LM Studio server")
        return False
    
    # Test chat completion
    chat_data = {
        "model": "local-model",
        "messages": [{"role": "user", "content": "Say 'Hello World' in Python"}],
        "max_tokens": 50
    }
    
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=chat_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Chat completion successful:")
        #print(result['choices']['message']['content'])
        print(result)
        print(result['choices'][0]['message']['content'])
        
        
        
        return True
    else:
        print(f"❌ Chat completion failed: {response.status_code}")
        return False

if __name__ == "__main__":
    test_lm_studio()
