ARG PYTHON_VERSION=3.13.7
FROM python:${PYTHON_VERSION}-slim as base

RUN mkdir /app
 
WORKDIR /app
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
RUN pip install --upgrade pip 
 
COPY requirements.txt  /app/
 
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . /app/
 
EXPOSE 8000

# CMD gunicorn --bind=0.0.0.0:8000 BagheeraCarrom.wsgi:application
CMD [ "uvicorn", "BagheeraCarrom.asgi:application" ]