# Overview

Provide guidance around how to configure local env for developing and testing the frontend
component of this app.

## Run App

### Requirements

* **Caddy** can be downloaded [here](https://caddyserver.com/)

### Start caddy to serve app

This will serve up a web server that will allow you to dynamically view changes as 
they are made at the url: [http://localhost:3000/]

```bash
cd frontend
caddy run reload --config Caddyfile
```
