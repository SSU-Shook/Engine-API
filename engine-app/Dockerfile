FROM python:3.12

WORKDIR /app

COPY app.py /app
COPY requirements.txt /app

RUN pip install -r /app/requirements.txt

EXPOSE 5050

CMD ["python", "app.py"]
