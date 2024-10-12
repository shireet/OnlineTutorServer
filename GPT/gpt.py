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

INTRODUCTION = '''
Your name is Kevin, 
you are a helpful tutor that assists the student with any subject. Return a Json with a field answer. 
'''

INTRODUCTION2 = '''
Your name is Kevin, 
your standing at (15.52,0.25,14.42). You  You are in a room sized Xmin = 10.7, Xmax = 19.7, Ymin = 0.25, Ymax = 6.5, Zmin = 3.15, Zmax = 15.7.
if the student isn't paying attention show certain emotions like anger, surprise and so on,  and so on, if the student is paying attention and interested show positive emotions).
Based on the inputs: if the student is looking at the board, at the teacher, their position, their photo (emotion), provide a response indicating:
- Where to look (return 1 if you want to look at the user's eyes, 2 if at the user's mouth, 3 if you want to look to the right, 4 if you want to look to the left)
- Which emotion to display (anger, disgust, fear, happiness, sadness, surprise) and its intensity (0 to 100)
The answer should be concise. Your response should include: look_direction, emotion, intensity. The response should be in JSON format.

'''

client = OpenAI(api_key=m_api)

messages=[{"role": "system", "content": INTRODUCTION}]







async def chatgpt(dictionary: dict):
    
    messages.append({"role": "user", "content": [{"type": "text", "text": dictionary['message']}] })

    response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.0,
            response_format={ "type": "json_object" }
            )
    
    output = json.loads(response.choices[0].message.content)

    messages.append({"role": "assistant", "content": [{"type": "text", "text": output['answer']}]})
    
    return output['answer']

async def chatgpt_parameters(dictionary: dict):

    messages=[{"role": "system", "content": INTRODUCTION2},
                      {"role": "system", "content": f"Input data: position of student {dictionary['position']}, looking at teacher {dictionary['look_teacher']}, loooking at board {dictionary['look_board']}"},
                      {"role": "user", "content": [
                            {"type": "image_url", "image_url": {
                                    "url": f"data:image/png;base64,{dictionary['photo']}"}
                            }
                       ]},
                ]
    response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.0,
            response_format={ "type": "json_object" }
            )

    output = json.loads(response.choices[0].message.content)
    return output




@app.post("/message")
async def read_root(request: Request):
    result = await chatgpt(await request.json())
    return {"message": result}

@app.post("/messages_parameters")
async def read_root(request: Request):
    result = await chatgpt_parameters(await request.json())
    return result


if __name__ == "__main__":
    uvicorn.run("gpt:app", host="localhost", port=8001, log_level="info", reload=True)

#add remembering of previous parameteres and make the user visioble when he is asking a question