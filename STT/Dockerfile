FROM python:3.10.11

WORKDIR /app

COPY stt/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stt /app

EXPOSE 8081

CMD ["uvicorn", "stt:app", "--host", "localhost", "--port", "8081"]
