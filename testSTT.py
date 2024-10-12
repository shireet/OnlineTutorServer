import requests
import base64

with open("1.wav", "rb") as file:
    encoded_audio = base64.b64encode(file.read()).decode('utf-8') 

payload = {
    "audio_base64": encoded_audio  
}

result = requests.post("http://localhost:8081/transcribe/", json=payload)

if result.status_code == 200:
    print(result.json().get('text'))
else:
    print(f"Error: {result.status_code}, {result.text}")
