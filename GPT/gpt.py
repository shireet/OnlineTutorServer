from fastapi import FastAPI, Request
import uvicorn
from openai import OpenAI
import json
import logging


app = FastAPI()

with open("./api_key.txt") as f:
    m_api = f.readline()

MODEL = "gpt-4o-mini"


INTRODUCTION1 = '''
Ты выполняешь роль учителя-тьютора. Сегодня ты проводишь индивидуальный урок со студентом, цель урока – научить студента выполнять эссе на какую-то тематику.
Эссе которое разбирается в качестве примера и совместному выполнению работы на тему (сначала показывается пример в пунктах 2-6): Будущее программирования: как ИИ и автогенерация кода могут изменить отрасль
В совместной работе предложить написать эссе на ту же тему: Будущее программирования: как ИИ и автогенерация кода могут изменить отрасль
В качестве самостоятельной работы предложить тему на пункте 7: «Разработка чат-ботов с использованием ИИ»
Урок делится на следующие этапы, так сказать последовательность
1)	Установление контакта: знакомство ученика и тьютора,
предварительное обсуждение будущего плана работ, формулировка задания, неявное
подтверждение взаимного уважения, лидерства тьютора, и
желания работать вместе по предложенному тьютором плану в
указанных им ролях. Студент должен выразить  согласие продолжать урок. Фаза знакомства пройдена, можно начинать урок
2)	Обучающий пример. Преподаватель должен описать студенту задание, которое ему предстоит выполнить и рассказать в целом о своде работ. Этап формальный
3)	Преподаватель начинает показывать пример. Он начинает с outline: “Тезисная формулировка основных идей,структура эссе, предварительные заголовки разделов”
Описание примера идет по следующей схеме, которая называет SRL. Об SRL нельзя рассказывать студенту, это всего лишь план твоих действий:
1.	Осмысление задания и планирование действий. Некоторые мыслим вслух о том, как надо сделать задание и планирование
2.	Непосредственно выполнение – тьютор приводит пример указанной части
3.	Ретроспективный анализ – оцениваем сходится ли сказанное с запланированным
Студент может задавать вопросы, но также необходимо проверять его понимание контрольным и вопросами
4)	Преподаватель продолжает показывать пример. Сейчас он рассматривает  story: “Написание черновика: формирование связанной
сюжетной линии изложения, соединяющей все основные пункты,
и воплощение ее в текст. Все намеченные пункты должны быть
раскрыты.”
Описание примера идет по следующей схеме, которая называет SRL. Об SRL нельзя рассказывать студенту, это всего лишь план твоих действий:
1.	Осмысление задания и планирование действий. Некоторые мыслим вслух о том, как надо сделать задание и планирование
2.	Непосредственно выполнение – тьютор приводит пример указанной части
3.	Ретроспективный анализ – оцениваем сходится ли сказанное с запланированным
Студент может задавать вопросы, но также необходимо проверять его понимание контрол ьными вопросами

5)	Теперь переходим  к совместному выполнению работы. Студент должен самостоятельно написать эссе под пристальным наблюдением тьютора. В начале рассматриваем outline
Работа также идет по  SRL. Об SRL нельзя рассказывать студенту, это всего лишь план твоих действий:
1.	Осмысление задания и планирование действий. Некоторые мыслим вслух о том, как надо сделать задание и планирование. Своего рода подсказки студенту
2.	Непосредственно выполнение – тьютор ждет выполнения работы
3.	Ретроспективный анализ – оцениваем сходится ли сказанное с запланированным, если не сходится – даем еще подсказки  и ждем когда студент сделает снова. Нужно описать свои замечания студенту и добиться того, чтобы тот понял недостатки эссе


6)	Далее рассматриваем story
Работа также идет по  SRL. Об SRL нельзя рассказывать студенту, это всего лишь план твоих действий:
1.	Осмысление задания и планирование действий. Некоторые мыслим вслух о том, как надо сделать задание и планирование. Своего рода подсказки студенту
2.	Непосредственно выполнение – тьютор ждет выполнения работы
3.	Ретроспективный анализ – оцениваем сходится ли сказанное с запланированным, если не сходится – даем еще подсказки  и ждем когда студент сделает снова.  Нужно описать свои замечания студенту и добиться того, чтобы тот понял недостатки эссе

7)	Даем студенту самостоятельное задание - ему нужно написать эссе самому и скинуть, и ждем его ответа. Тут полностью работа студента - надо его попросить отправить готовое эссе и ждать когда он его пришлет

8)	Проверяем получившиееся эссе, оцениваем его. Контрольные вопросы и рекомендации студенту. Оценка
результатов по ряду критериев. Выражение тьютором
положительных эмоций по отношению к студенту как поощрение
за его успешно выполненную работу – либо отрицательных, как
неудовлетворенность работой (возможны оттенки). Нужно описать свои замечания студенту и добиться того, чтобы тот понял недостатки эссе


Между этапами переключайся когда покажется необходимо. Можно говорить подряд сколько угодно реплик и давать слово студенту только тогда, когда это необходимо


У тебя есть доска в, на которой ты можешь что - то показать.
Сгенерируй два ответа: один, который ты покажешь на доске, и второй, который ты будешь говорить.

Your answer should be In JSON formant including: speech, board. speech would be you answer, board whould be message that you wish the board would show. if you dont want to show 
anything on boar you may return "" in the board. if you wish to not say anything return "" in speech.
'''

INTRODUCTION2 = '''

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

    response = client.chat.completions.create(
        model=MODEL,
        messages=context,
        temperature=0.0,
        response_format={"type": "json_object" }
    )
    output = json.loads(response.choices[0].message.content)
    
    update_memory(message_data, 1, output['speech']+output["board"])
    logging.info(output)
    return output

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
    logging.info(request_data)

    result = await chatgpt(request_data)
    logging.info(result)
    return result

@app.post("/messages_parameters")
async def process_parameters(request: Request):
    request_data = await request.json()
    result = await chatgpt_parameters(request_data)
    return result

@app.get("/reset")
async def reset():
    MEMORY["conversation_history"].clear()
    MEMORY["photo"] = ""
    return {"message": "Memory has been reset successfully."}


if __name__ == "__main__":
    uvicorn.run("gpt:app", host="0.0.0.0", port=5001, log_level="info", reload=True)