import requests, os

url = "https://api.openrouter.ai/v1/models"
headers = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"}
resp = requests.get(url, headers=headers, timeout=10)
print(resp.status_code, resp.text)
