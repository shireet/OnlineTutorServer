import requests
import base64



with open("audio/1.wav", "rb") as file:
    encoded_audio = base64.b64encode(file.read()).decode('utf-8') 

payload = {
    "audio_base64": encoded_audio  
}

result = requests.post("http://127.0.0.1:5000/speech", json=payload)

if result.status_code == 200:
    with open("audio/testServer.wav", "wb") as audio:
        print("bananas")
        audio.write(base64.b64decode(result.json().get('audio_base64')))
else:
    print(f"Error: {result.status_code}, {result.text}")
