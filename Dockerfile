ARG PYTHON_VERSION=3.13.7
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /BagheeraCarrom

RUN apt-get update && apt-get install -y \ 
    build-essential \
    pkg-config \
    default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER appuser

COPY . .

EXPOSE 8000

# CMD gunicorn --bind=0.0.0.0:8000 BagheeraCarrom.wsgi:application
CMD [ "uvicorn", "BagheeraCarrom.asgi:application" ]