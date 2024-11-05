FROM python:3.9.1

WORKDIR /app

COPY . /app/chat

RUN pip install --no-cache-dir -r /app/chat/requirements.txt

CMD ["uvicorn", "chat.main:app", "--host", "0.0.0.0", "--port", "8001"]
