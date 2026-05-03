ARG PYTHON_VERSION=3.13.1

FROM python:${PYTHON_VERSION}-slim-bookworm AS python

FROM python AS python-build-stage

RUN apt-get update && apt-get install \
    --no-install-recommends -y \
    build-essential \
    libpq-dev

COPY ./backend/requirements.txt .

RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r requirements.txt \
    --no-cache-dir