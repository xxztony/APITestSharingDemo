FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/app/generated

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p app/generated && \
    python -m grpc_tools.protoc \
      -I proto \
      --python_out=app/generated \
      --grpc_python_out=app/generated \
      proto/pricing.proto

EXPOSE 50051
CMD ["python", "-m", "app.server"]

