import requests
import base64

result = requests.post("http://localhost:8082/speech", json={'text': "Hello my name is Kevin"})


audio_base64 = result.json().get('audio_base64')


with open("test.wav", "wb") as audio:
   audio.write(base64.b64decode(audio_base64))

