FROM python:3.12

WORKDIR /app

COPY app.py /app
COPY database.py /app
COPY models.py /app
COPY schemas.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "app.py"]