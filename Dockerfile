FROM python:3.7.3-slim-stretch

WORKDIR /app
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=plugserv.settings

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD docker-archive.tar ./

RUN groupadd --gid 499 plugserv \
  && useradd --uid 497 --gid plugserv --shell /bin/bash --create-home plugserv
USER plugserv:plugserv
CMD ["gunicorn", "--worker-class", "gevent", "plugserv.wsgi", "-b", "0.0.0.0:8000"]
