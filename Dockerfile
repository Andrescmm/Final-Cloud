# Version peque de python
FROM python:3

ENV PYTHONUNBUFFERED true

# coppy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# install dependencies
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Corremos el servicio en un container startup. Aqui usamos gunicorn
# 1 worker process y 8 threads.


CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app