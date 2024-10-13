import tempfile
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import uvicorn

with open("./api_key.txt") as f:
    m_api = f.readline().strip()

client = OpenAI(api_key=m_api)

app = FastAPI()

class TextRequest(BaseModel):
    text: str

async def text_to_speech(input_text: str, model: str = "tts-1", voice: str = "onyx"):
    try:
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=input_text
        ) as response:
            audio_path = './audio/'
            os.makedirs(audio_path, exist_ok=True)  # Ensure the directory exists
            
            with tempfile.NamedTemporaryFile(prefix='ans_', 
                                             suffix='.wav', 
                                             dir=audio_path, 
                                             delete=False) as temp_file:
                response.stream_to_file(temp_file.name)
                return temp_file.name

    except Exception as e:
        print(f"An error occurred while synthesizing speech: {e}")
        return None

async def encode_audio_to_base64(audio_file_path: str) -> str:
    try:
        with open(audio_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
            # Encode the audio data as base64
            encoded_audio = base64.b64encode(audio_data).decode("utf-8")
            return encoded_audio
    except Exception as e:
        print(f"Error encoding audio file: {e}")
        return None


@app.post("/speech")
async def handle_text_to_speech(request: TextRequest):
    try:
        text = request.text
        if not text:
            raise HTTPException(status_code=400, detail="Invalid text input")

        audio_file_path = await text_to_speech(text)
        if not audio_file_path:
            raise HTTPException(status_code=500, detail="Failed to generate speech")

        encoded_audio = await encode_audio_to_base64(audio_file_path)
        if not encoded_audio:
            raise HTTPException(status_code=500, detail="Failed to encode audio to base64")

        return JSONResponse(content={"audio_base64": encoded_audio})

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == '__main__':
    uvicorn.run("tts:app", host="0.0.0.0", port=5003, log_level="info", reload=True)

