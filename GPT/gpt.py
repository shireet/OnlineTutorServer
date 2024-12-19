from fastapi import FastAPI, Request, HTTPException
import uvicorn
from openai import OpenAI
import json

app = FastAPI()

with open("./api_key.txt") as f:
    m_api = f.readline()

MODEL = "gpt-4o-mini"

with open("./prompt_verbal.txt", "r") as f:
    INTRODUCTION_VERBAL = f.read()

with open("./prompt_not_verbal.txt", "r") as f:
    INTRODUCTION_NOT_VERBAL = f.read()

client = OpenAI(api_key=m_api)

client_memories = {}

def get_memory(client_id):
    if client_id not in client_memories:
        client_memories[client_id] = {
            "conversation_history": [], 
            "photo": ""
        }
    return client_memories[client_id]

def update_memory(client_id, data, flag, response=None):
    memory = get_memory(client_id)
    if flag == 1:
        memory["conversation_history"].append({"user": data["message"], "assistant": response})
    elif flag == 2:
        if data.get("photo_base64"):
            memory["photo_base64"] = data["photo_base64"]

async def chatgpt(client_id, message_data):
    memory = get_memory(client_id)
    
    context = [{"role": "system", "content": INTRODUCTION_VERBAL}]
    
    for exchange in memory["conversation_history"]:
        context.append({"role": "user", "content": exchange["user"]})
        context.append({"role": "assistant", "content": exchange["assistant"]})
    
    context.append({"role": "user", "content": message_data["message"]})

    response = client.chat.completions.create(
        model=MODEL,
        messages=context,
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    output = json.loads(response.choices[0].message.content)
    
    update_memory(client_id, message_data, 1, output['speech'] + output["board"])
    return output


async def chatgpt_parameters(client_id, data):
    update_memory(client_id, data, 2)

    memory = get_memory(client_id)
    context = [
        {"role": "system", "content": INTRODUCTION_NOT_VERBAL},
        {"role": "system", "content": f"Input data: position {data['position']}, look at teacher {data['is_looking_teacher']}, look at board {data['is_looking_board']}"},
    ]
    context.append({"role": "user", "content": [
        {"type": "image_url", "image_url": {
            "url": f"data:image/png;base64,{memory['photo']}"
            }
        }
    ]})

    response = client.chat.completions.create(
        model=MODEL,
        messages=context,
        temperature=0.7,
        response_format={ "type": "json_object" }
    )
    output = json.loads(response.choices[0].message.content)
    return output

@app.post("/{client_id}/message")
async def process_message(client_id: int, request: Request):
    request_data = await request.json()
    result = await chatgpt(client_id, request_data)
    return result

@app.post("/{client_id}/messages_parameters")
async def process_parameters(client_id: int, request: Request):
    request_data = await request.json()
    result = await chatgpt_parameters(client_id, request_data)
    return result

@app.get("/{client_id}/reset")
async def reset(client_id: int):
    memory = get_memory(client_id)
    memory["conversation_history"].clear()
    memory["photo"] = ""
    return {"message": "Memory has been reset successfully."}

if __name__ == "__main__":
    uvicorn.run("gpt:app", host="0.0.0.0", port=5001, log_level="info", reload=True)
