from fastapi import FastAPI, Request
import asyncio
import uvicorn
from openai import OpenAI
import json
import base64


app = FastAPI()

with open("./api_key.txt") as f:
    m_api = f.readline()

MODEL = "gpt-4o-mini"


INTRODUCTION1 = '''
Your name is Kevin, 
you are a helpful tutor that assists the student with any subject. 
if the student asks a question or says a phrase give an answer. Ther response should be in json format with a field 'answer'
Also you will be sent an image of the student.
'''

INTRODUCTION2 = '''
Your name is Kevin, 
you are a helpful tutor that assists the student with any subject. 
if the student is looking at the board, at the teacher, their position,  their photo (identify their emotional status), provide a response indicating:
- Where to look (return 1 if you want to look at the user's eyes, 2 if at the user's mouth, 3 if you want to look to the right, 4 if you want to look to the left)
- Which emotion to display (anger, disgust, fear, happiness, sadness, surprise) and its intensity (0 to 100)
Your response should include: look_direction, emotion, intensity. The response should be in JSON format.
'''

MEMORY = {
    "conversation_history": [], 
    "photo": ""             
}

client = OpenAI(api_key=m_api)

def update_memory(data, flag, response=None):
    if flag == 1:
        MEMORY["conversation_history"].append({"user": data["message"], "assistant": response})
    elif flag == 2:
        if data.get("photo"):
            MEMORY["photo"] = data["photo"]


async def chatgpt(message_data):

    context = [{"role": "system", "content": INTRODUCTION1}]
    
    for exchange in MEMORY["conversation_history"]:
        context.append({"role": "user", "content": exchange["user"]})
        context.append({"role": "assistant", "content": exchange["assistant"]})
    
    context.append({"role": "user", "content": message_data["message"]})

    context.append({"role": "user", "content": [
        {"type": "image_url", "image_url": {
            "url": f"data:image/png;base64,{MEMORY['photo']}"
            }
        }
    ]})

    response = client.chat.completions.create(
        model=MODEL,
        messages=context,
        temperature=0.0,
        response_format={"type": "json_object" }
    )
    output = json.loads(response.choices[0].message.content)
    
    update_memory(message_data, 1, output['answer'])
    
    return output['answer']

async def chatgpt_parameters(data):
    update_memory(data,2)

    context = [
        {"role": "system", "content": INTRODUCTION2},
        {"role": "system", "content": f"Input data: position {data['position']}, look at teacher {data['look_teacher']}, look at board {data['look_board']}"},
    ]
    context.append({"role": "user", "content": [
        {"type": "image_url", "image_url": {
            "url": f"data:image/png;base64,{MEMORY['photo']}"
            }
        }
    ]})

    response = client.chat.completions.create(
        model=MODEL,
        messages=context,
        temperature=0.0,
        response_format={ "type": "json_object" }
    )
    output = json.loads(response.choices[0].message.content)
    return output

@app.post("/message")
async def process_message(request: Request):
    request_data = await request.json()
    result = await chatgpt(request_data)
    return {"message": result}

@app.post("/messages_parameters")
async def process_parameters(request: Request):
    request_data = await request.json()
    result = await chatgpt_parameters(request_data)
    return result

if __name__ == "__main__":
    uvicorn.run("gpt:app", host="0.0.0.0", port=5001, log_level="info", reload=True)