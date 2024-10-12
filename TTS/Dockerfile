FROM python:3.10.11

WORKDIR /app

COPY tts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tts /app

EXPOSE 8082

CMD ["uvicorn", "tts:app", "--host", "localhost", "--port", "8082"]
