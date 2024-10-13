import tempfile
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import uvicorn

with open("./api_key.txt") as f:
    m_api = f.readline().strip()

client = OpenAI(api_key=m_api)

app = FastAPI()

class AudioRequest(BaseModel):
    audio_base64: str

async def transcribe(audio):
    try:
        with tempfile.NamedTemporaryFile(prefix='req_', suffix='.wav', delete=False) as temp_audio_file:
            temp_audio_file.write(audio)
            temp_audio_file_path = temp_audio_file.name

            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp_audio_file_path, 'rb')
            )
        temp_audio_file.close()

        transcription_text = transcription_response['text'] if isinstance(transcription_response, dict) else transcription_response.text

        return transcription_text

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

@app.post("/transcribe/")
async def handle_speech_to_text(request: AudioRequest):
    try:
        audio_data = base64.b64decode(request.audio_base64)

        if not audio_data:
            raise HTTPException(status_code=400, detail="Invalid base64 audio data")

        transcription = await transcribe(audio_data)
        print(transcription)

        if transcription is None:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")

        return JSONResponse(content={"text": transcription})

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == '__main__':
    uvicorn.run("stt:app", host="0.0.0.0", port=5002, log_level="info", reload=True)

