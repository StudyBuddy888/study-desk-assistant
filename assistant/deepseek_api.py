import requests
from config import DEEPSEEK_API_KEY

def deepseek_query(text):
    """Send user query to DeepSeek API"""
    url = "https://api.deepseek.com/v1/assistant"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"input": text}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get("output", "I couldn't process that.")
    return "Error in processing request."
