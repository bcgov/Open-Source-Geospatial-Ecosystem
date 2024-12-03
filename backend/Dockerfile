FROM python:3.11-alpine as base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN apk update && \
    apk add libpq


FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apk update && \
    apk add musl-dev build-base gcc gfortran openblas-dev gdal gdal-dev proj proj-util proj-dev geos geos-dev

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.4

# Install the app
COPY pyproject.toml poetry.lock ./
RUN if [ $DEV ]; then \
      poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    else \
      poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi


FROM base as runtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
RUN apk add bash gdal proj geos

COPY . ./app

WORKDIR /app

ENTRYPOINT ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "osgeo_app.main:gunicorn_app"]
