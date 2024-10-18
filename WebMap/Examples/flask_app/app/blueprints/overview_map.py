from flask import Blueprint, request, render_template, jsonify, make_response
import geopandas as gpd
import os

#get saved html map
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(BASE_DIR,  '..', 'static', 'LUP_Overview.html')


blueprint=Blueprint("Overview_Map", __name__)

@blueprint.route("/overview_map")
def overview():
    with open(map_path, 'r') as f:
        folium_map = f.read()
    return render_template("overview.html", folium_map=folium_map,),200