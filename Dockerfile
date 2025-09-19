ARG PYTHON_VERSION=3.13.7
FROM python:${PYTHON_VERSION}-slim as base

RUN mkdir /BagheeraCarrom
 
WORKDIR /BagheeraCarrom
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
RUN pip install --upgrade pip 
 
COPY requirements.txt  /BagheeraCarrom/
 
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . /BagheeraCarrom/
# RUN mkdir -p /BagheeraCarrom/staticfiles
# RUN mkdir -p /BagheeraCarrom/media 

# RUN groupadd -r django && useradd -r -g django django
# RUN chown -R django:django /BagheeraCarrom
# USER django

EXPOSE 8000

# CMD ["uvicorn", "BagheeraCarrom.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
CMD ["gunicorn", "BagheeraCarrom.wsgi:application", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keepalive", "5"]