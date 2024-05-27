FROM python:3.12

WORKDIR /app

COPY app.py /app
COPY database.py /app
COPY models.py /app
COPY schemas.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt-get update && apt-get install -y git wget

WORKDIR /codeql

RUN wget https://github.com/github/codeql-cli-binaries/releases/download/v2.17.3/codeql-linux64.zip -O codeql-cli.zip
RUN unzip codeql-cli.zip -d codeql-cli
RUN git clone https://github.com/github/codeql codeql-repo

# RUN export PATH=$PATH:/codeql/codeql-cli/codeql

RUN echo "export PATH=$PATH:/codeql/codeql-cli/codeql" >> ~/.bashrc
RUN source ~/.bashrc

WORKDIR /app

# EXPOSE 5000
CMD ["python", "/app/app.py"]