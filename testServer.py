import requests
import base64
import os



with open("audio/1.wav", "rb") as file:
    encoded_audio = base64.b64encode(file.read()).decode('utf-8') 

payload = {
    "audio_base64": encoded_audio  
}

result = requests.post("http://localhost:8000/speech", json=payload)

if result.status_code == 200:
    with open("audio/testServer.wav", "wb") as audio:
        audio.write(base64.b64decode(result.json().get('audio_base64')))
else:
    print(f"Error: {result.status_code}, {result.text}")
