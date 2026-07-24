FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for lxml; kept minimal.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Playwright is optional at runtime; install the wheel but skip the browser
# download here (only needed if you enable render_js on a source).
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
