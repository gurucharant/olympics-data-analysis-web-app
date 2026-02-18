FROM python:3.11-slim

WORKDIR /app

# Install system deps (small, safe defaults)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run listens on $PORT (usually 8080)
ENV PORT=8080

# Streamlit config for Cloud Run
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=$PORT
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
