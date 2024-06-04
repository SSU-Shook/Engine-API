FROM python:3.12

RUN apt-get update && apt-get install -y git wget

WORKDIR /codeql

RUN wget https://github.com/github/codeql-cli-binaries/releases/download/v2.17.3/codeql-linux64.zip -O codeql-cli.zip
RUN unzip codeql-cli.zip -d codeql-cli
RUN git clone https://github.com/github/codeql codeql-repo

RUN rm -rf /codeql/codeql-repo/javascript/ql/src/Security/CWE-020

ENV PATH /codeql/codeql-cli/codeql:$PATH

WORKDIR /app

COPY app.py /app
COPY database.py /app
COPY models.py /app
COPY schemas.py /app
COPY config.py /app
COPY requirements.txt /app
COPY patch_utils.py /app
COPY sast_llm.py /app
COPY instructions.py /app
COPY helper_utils.py /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# EXPOSE 5000
CMD ["python", "/app/app.py"]