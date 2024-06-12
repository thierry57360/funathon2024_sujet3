ARG BASE_IMAGE=python:3.11-slim
FROM $BASE_IMAGE

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
    
COPY correction/ .
    
EXPOSE 5000
    
HEALTHCHECK CMD curl --fail http://localhost:5000/_stcore/health
    
ENTRYPOINT ["python", "main.py"]
