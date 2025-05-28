FROM python:3.11-slim
WORKDIR /app
COPY notes_mcp_server.py mcp_settings.py .
RUN pip install fastapi uvicorn gitpython
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
