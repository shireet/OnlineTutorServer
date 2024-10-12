FROM python:3.10.11

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api /app

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "localhost", "--port", "8000"]
