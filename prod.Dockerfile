FROM cutktweaks:v1.3

WORKDIR /home/cutktweaks-app/app

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

