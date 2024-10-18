from flask import Blueprint, request, render_template, jsonify, make_response
import geopandas as gpd
import os
import logging
import folium
import tempfile
from io import BytesIO
import feature_download
import fiona

# Enable fiona driver for KML support
fiona.drvsupport.supported_drivers['libkml'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

logging.basicConfig(level=logging.INFO)

# Initialize WFS downloader
wfs = feature_download.WFS_downloader()

# Load the local geojson AOI file and get bbox in Albers projection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

lup_aoi = os.path.join(BASE_DIR,'..','..','data', 'geojson', 'aoi.geojson')
aoi = gpd.read_file(lup_aoi)
bbox_albers = wfs.create_bbox(aoi)
aoi = aoi.to_crs(4326)  # Transform AOI to WGS 84

# WFS layer fetcher
def wfs_getter(layer, bbox=None):
    wfs_layer = wfs.get_data(layer, bbox=bbox)
    wfs_layer = wfs_layer.set_crs('epsg:3005').to_crs(4326)
    return wfs_layer

# Fetch the RMP_LG_PLY WFS layer
RMP_LG_PLY = wfs_getter("WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW", bbox=bbox_albers)

# Set map starting parameters
lon, lat = -128.867888, 55.781113
zoom_start = 7
basemap = "OpenStreetMap"

# Blueprint registration
blueprint = Blueprint("Intersect", __name__)

# Function to create Folium map
def create_map_html(input_gdf=None, intersected_gdf=None):
    m = folium.Map(location=[lat, lon], tiles=basemap, zoom_start=zoom_start, control_scale=True)
    
    # Add layers to the map
    folium.GeoJson(RMP_LG_PLY, name="Legal Planning Objectives - Polygon",
                   style_function=lambda feature: {"fillColor": "transparent", "color": "red", "weight": 1}).add_to(m)
    folium.GeoJson(aoi, name="Area of Interest",
                   style_function=lambda feature: {"fillColor": "transparent", "color": "blue", "weight": 4}).add_to(m)

    # Add intersected and input layers if they exist
    if intersected_gdf is not None:
        folium.GeoJson(intersected_gdf, name="Intersected Layer",
                       style_function=lambda feature: {"fillColor": "transparent", "color": "green", "weight": 2}).add_to(m)

    if input_gdf is not None:
        folium.GeoJson(input_gdf, name="Uploaded Layer",
                       style_function=lambda feature: {"fillColor": "transparent", "color": "purple", "weight": 2}).add_to(m)

    return m._repr_html_()  # Return the map as HTML to embed in the page

# Route to handle file upload, intersection, and map rendering
@blueprint.route("/intersect", methods=["GET", "POST"])
def intersect():
    input_gdf = None
    intersected_gdf = None
    map_html = None
    intersected_data = None


    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return "No file uploaded", 400

        # Read uploaded file in memory
        file_bytes = BytesIO(uploaded_file.read())
        
        # Load the file into GeoPandas based on file type
        try:
            if uploaded_file.filename.endswith(".geojson"):
                input_gdf = gpd.read_file(file_bytes)
            elif uploaded_file.filename.endswith(".shp"):
                input_gdf = gpd.read_file(file_bytes)
            elif uploaded_file.filename.endswith(".kml"):
                input_gdf = gpd.read_file(file_bytes, driver="libkml")
            else:
                return "Unsupported file type", 400
            input_gdf = input_gdf.to_crs(4326)
        except Exception as e:
            return f"Error reading the file: {str(e)}", 500

        # Perform spatial join
        # need to drop columns from input_gdf and probably lots from the landuse poly
        try:
            intersected_gdf = gpd.sjoin(RMP_LG_PLY, input_gdf, how='inner', predicate='intersects')
            #need to drop geometry column and probably others
            intersected_data = intersected_gdf.to_dict(orient='records')
        except Exception as e:
            return f"Error during intersection: {str(e)}", 500

    # Create the map after intersection
    map_html = create_map_html(input_gdf, intersected_gdf)
    logging.info(f"Map HTML: {map_html}")
    
    # If no data is intersected, pass an empty list
    if not intersected_data:
        intersected_data = []

    # Render the form, map, and table on the same page
    return render_template("intersect_template.html", map_html=map_html, intersected_data=intersected_data)


@blueprint.route("/download_csv")
def download_csv():
    # Return CSV download for intersected_gdf
    global intersected_gdf
    csv_data = intersected_gdf.to_csv(index=False)
    
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=intersected_data.csv"
    response.headers["Content-Type"] = "text/csv"
    
    return response