# Overview

Provide guidance around how to configure local env for developing and testing the frontend
component of this app.

## Run App - Caddy

### Requirements

* **Caddy** can be downloaded [here](https://caddyserver.com/)

### Start caddy to serve app

This will serve up a web server that will allow you to dynamically view changes as 
they are made at the url: [http://localhost:3000/]

```bash
cd frontend
export LOG_LEVEL=DEBUG
caddy run reload --config Caddyfile
```

If you are running on windoze, replace `export LOG_LEVEL=DEBUG` with `SET LOG_LEVEL=DEBUG`

## Run App through Docker

This approach will package up the app into a docker image, and the run that
image.  Eventually this will get encorporated into Docker-compose.

### Build the image

``` bash
cd frontend
docker build -t osgeo .
```

### Run the image

`docker run -e LOG_LEVEL='DEBUG' -p 3000:3000 -t osgeo`
