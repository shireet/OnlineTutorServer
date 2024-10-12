import requests
import base64



with open("image/akmal.png", "rb") as file:
    encoded_image = base64.b64encode(file.read()).decode('utf-8') 

payload = {
    "position": {
        "x": 0,
        "y": 0,
        "z": 0
    },
    "is_looking_teacher": True,
    "is_looking_board": False,
    "photo_base64": encoded_image
}

result = requests.post("http://localhost:8000/parameters", json=payload)

if result.status_code == 200:
    print(result.json())
else:
    print(f"Error: {result.status_code}, {result.text}")
