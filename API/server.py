from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.responses import JSONResponse
import aiohttp
from pydantic import BaseModel

URL_GPT = "http://localhost:8001"
URL_SST = "http://localhost:8081"
URL_TTS = "http://localhost:8082"

app = FastAPI()

class AudioRequest(BaseModel):
    audio_base64: str



@app.post("/speech")
async def speech(request: AudioRequest):
    try:
        audio_data = request.audio_base64
        if not audio_data:
            raise HTTPException(status_code=400, detail="Invalid base64 audio data")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{URL_SST}/transcribe/", json={"audio_base64": audio_data}) as stt_response:
                if stt_response.status == 200:
                    stt_response_data = await stt_response.json()  
                    audio_text = stt_response_data.get('text')
                else:
                    print("Problem with STT")
                    raise HTTPException(status_code=stt_response.status, detail=stt_response.text)

            async with session.post(f"{URL_GPT}/message", json={"message": audio_text}) as gpt_response:
                if gpt_response.status == 200:
                    gpt_response_data = await gpt_response.json()  
                    gpt_response_text = gpt_response_data.get('message')  
                else:
                    print("Problem with GPT")
                    raise HTTPException(status_code=gpt_response.status, detail=gpt_response.text)
                
            async with session.post(f"{URL_TTS}/speech", json={'text': gpt_response_text}) as tts_response:
                if tts_response.status == 200:
                    tts_response_data = await tts_response.json() 
                    tts_audio_base64 = tts_response_data.get('audio_base64')  
                else:
                    print("Problem with TTS")
                    raise HTTPException(status_code=tts_response.status, detail=tts_response.text)
                
        return JSONResponse(content={"audio_base64": tts_audio_base64})  

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")   

@app.post("/parameters")
async def parameters()
     

if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000, log_level="info", reload=True)
