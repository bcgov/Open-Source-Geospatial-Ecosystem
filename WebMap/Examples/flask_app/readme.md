# Flask Test App
flask app that can load a geojson (more formats to come) and intersect it with legal land use poloygons, refresh the page to show the input data, intersected features and the table below with option to download as csv

## Instructions using docker
1. change directory to WebMap/flask_app
2. ```docker build -t wm-flask```
3. ```docker run -p 5000:5000 wm-flask```

```<ctrl>c``` to exit or you can use ```docker run -d -p 5000:5000 wm-flask``` to detach docker from the terminal. 

## To run
- open cmd or terminal
- cd to flask_app folder
- python -m app 
- in web browser enter http://localhost:5000/intersect
