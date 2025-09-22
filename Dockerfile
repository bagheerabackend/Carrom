ARG PYTHON_VERSION=3.12.0
FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r django && useradd -r -g django django

WORKDIR /BagheeraCarrom

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY --chown=django:django requirements.txt /BagheeraCarrom/
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=django:django . /BagheeraCarrom/

RUN chown -R django:django /BagheeraCarrom && chmod -R u+rw /BagheeraCarrom

USER django

EXPOSE 8000

CMD ["gunicorn", "BagheeraCarrom.wsgi:application", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keepalive", "5"]