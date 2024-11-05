FROM python:3.9.1

WORKDIR /app

COPY . /app/website

RUN pip install --no-cache-dir -r /app/website/requirements.txt

CMD ["uvicorn", "website.main:app", "--host", "0.0.0.0", "--port", "8000"]
