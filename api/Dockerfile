FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=api.settings

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords averaged_perceptron_tagger

COPY . /app/

CMD ["uvicorn", "api.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
