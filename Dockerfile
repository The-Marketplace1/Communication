FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
WORKDIR /app
COPY src ./src
COPY migrations ./migrations
EXPOSE 8080
CMD ["python", "-m", "src.app.main"]
