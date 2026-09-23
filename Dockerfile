FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
# CLI tool: pass a URL and flags, e.g. docker run <img> https://example.com --fullpage
ENTRYPOINT ["python", "screenshot_engine.py"]
CMD ["--help"]
