# 1. Base Python image (Lightweight)
FROM python:3.10-slim

# 2. Container ke andar folder set karna
WORKDIR /app

# 3. DuckDB/Pandas ke liye basic Linux build tools install karna
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt copy karke dependencies install karna
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Apna saara project code container me copy karna
COPY . .

# 6. Render ka default port specify karna
EXPOSE 10000

# 7. FastAPI server start karne ki command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
