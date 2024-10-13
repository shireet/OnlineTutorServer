from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.responses import JSONResponse
import aiohttp
from pydantic import BaseModel

URL_GPT = "http://gpt:5001"
URL_SST = "http://stt:5002"
URL_TTS = "http://tts:5003"


app = FastAPI()

class AudioRequest(BaseModel):
    audio_base64: str
    
class ParametersRequest(BaseModel):
    position: dict
    photo_base64: str
    is_looking_teacher: bool
    is_looking_board: bool


async def post_request(url: str, data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise HTTPException(status_code=response.status, detail=await response.text())


@app.post("/speech")
async def speech(request: AudioRequest):
    try:
        if not request:
            raise HTTPException(status_code=400, detail="Invalid request data")   
        audio_data = request.audio_base64        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Invalid base64 audio data")

        # STT
        stt_response_data = await post_request(f"{URL_SST}/transcribe/", {"audio_base64": audio_data})
        audio_text = stt_response_data.get('text')
        if not audio_text:
            raise HTTPException(status_code=500, detail="No text returned from STT")

        # GPT
        gpt_response_data = await post_request(f"{URL_GPT}/message", {"message": audio_text})
        gpt_response_text = gpt_response_data.get('message')
        if not gpt_response_text:
            raise HTTPException(status_code=500, detail="No message returned from GPT")

        # TT
        tts_response_data = await post_request(f"{URL_TTS}/speech", {"text": gpt_response_text})
        tts_audio_base64 = tts_response_data.get('audio_base64')
        if not tts_audio_base64:
            raise HTTPException(status_code=500, detail="No audio returned from TTS")

        return JSONResponse(content={"audio_base64": tts_audio_base64})

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/parameters")
async def parameters(request: ParametersRequest):
    try:
        
        if not request:
            raise HTTPException(status_code=400, detail="Invalid request data")
        
        if not request.position:
            raise HTTPException(status_code=400, detail="Invalid locations")
        
        if not request.photo_base64:
            raise HTTPException(status_code=400, detail="Invalid base64 photo data")
        if request.is_looking_teacher is None or request.is_looking_board is None:
            raise HTTPException(status_code=400, detail="Invalid looking status")
        print("hi")
        
        gpt_response_data = await post_request(f"{URL_GPT}/messages_parameters", {
            "position": request.position,
            "look_teacher": request.is_looking_teacher,
            "look_board": request.is_looking_board,
            "photo": request.photo_base64
        })
        if not gpt_response_data:
            raise HTTPException(status_code=500, detail="No message returned from GPT")
        return JSONResponse(content=gpt_response_data)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return None


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
