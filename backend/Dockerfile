# FROM python:3.12-alpine as base
FROM python:3.12-slim-bookworm as base


ARG DEV=false
ENV VIRTUAL_ENV=/osgeo_app/docker_venv \
    PATH="/osgeo_app/docker_venv/bin:$PATH"

    
# -------------- STAGE 2 --------------

FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/osgeo_app/docker_venv \
    PATH="/osgeo_app/docker_venv/bin:$PATH"


# RUN apk update && \
#     apk add musl-dev build-base gcc gfortran openblas-dev gdal gdal-dev proj proj-util proj-dev geos geos-dev python3-dev musl-dev
RUN apt update && \
    apt install -y --no-install-recommends apt-utils gcc python3-dev libgeos-dev libproj-dev gdal-bin proj-data

WORKDIR /osgeo_app

# Install Poetry
RUN pip install poetry==1.8.5

# create the venv in $VIRTUAL_ENV so we can control where it is being created
#  unfortunately this is the only way that we can control the venv that
#  poetry will use, is to create it ourselves
RUN python -m venv $VIRTUAL_ENV; . $VIRTUAL_ENV/bin/activate

# Install the app
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip wheel setuptools
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR;

FROM base as runtime

ENV PROJ_LIB=/usr/share/proj

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
# RUN apk add bash gdal proj geos
RUN apt update && \
    apt install -y --no-install-recommends gdal-bin gdal-data gdal-plugins proj-bin proj-data geos-bin


COPY . ./osgeo_app

WORKDIR /osgeo_app

ENTRYPOINT ["python", "-m", "gunicorn", "--timeout", "2000","--bind", "0.0.0.0:5000", "--workers","4","osgeo_app.main:gunicorn_app"]
