FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN chown -R app:app /app

USER app

# Cambiamos a 8080 para que coincida con el estándar de Cloud Run
EXPOSE 8080

CMD ["sh", "-c", "gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60"]