FROM python:3.11.1-slim-bullseye as builder

WORKDIR /usr/src/app

COPY reqs-cutktweaks.txt .

RUN python3.11 -m venv /opt/venv; apt update; apt install gcc build-essential -y
ENV PATH=/opt/venv/bin:$PATH
RUN pip3.11 install -r reqs-cutktweaks.txt

FROM python:3.11.1-slim-bullseye

COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

ENV APP_HOME=/home/cutktweaks-app/app
RUN mkdir -p $APP_HOME; mkdir -p $APP_HOME/logs;

WORKDIR $APP_HOME

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

