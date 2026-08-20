FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

COPY . .

EXPOSE 8000

CMD ["python", "-m", "llm_search.main"]
