FROM python:3.10.11

WORKDIR /app

COPY gpt/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gpt /app

EXPOSE 8001

CMD ["uvicorn", "gpt:app", "--host", "localhost", "--port", "8001"]
