FROM cutktweaks:v1.1

WORKDIR /home/cutktweaks-app/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

