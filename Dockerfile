ARG PYTHON_VERSION=3.10
FROM python:$PYTHON_VERSION-slim

ENV BOT_TOKEN ""

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python"]

CMD ["bot.py"]
