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

COPY . /app/

RUN ulimit -n 4096 || true

RUN pip install gunicorn

# Use Gunicorn with gthread workers for Django (WSGI)
CMD ["gunicorn", "api.wsgi:application", "-b", "0.0.0.0:8000", "--workers=4", "--threads=8", "--timeout=60", "--access-logfile=-", "--error-logfile=-"]
