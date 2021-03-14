FROM python:3.7.9-slim-stretch

WORKDIR /app
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=plugserv.settings_prod

# https://github.com/nouchka/docker-sqlite3/blob/master/Dockerfile
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get -yq --no-install-recommends install sqlite3=3.* wget && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD app-archive.tar ./

CMD ["gunicorn", "--worker-class", "gevent", "plugserv.wsgi", "-b", "0.0.0.0:8000"]
