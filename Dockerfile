FROM python:3.9.20-slim-bookworm

WORKDIR /app
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=plugserv.settings_prod

# https://github.com/nouchka/docker-sqlite3/blob/master/Dockerfile
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get -yq --no-install-recommends install sqlite3=3.* wget && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY --from=ghcr.io/astral-sh/uv:0.7.21 /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache

ADD app-archive.tar ./

CMD ["uv", "run", "gunicorn", "--worker-class", "gevent", "plugserv.wsgi", "-b", "0.0.0.0:8000"]
