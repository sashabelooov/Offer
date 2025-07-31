FROM python:3.11-slim

WORKDIR /app

COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env .env

CMD ["python", "runbot.py"]
