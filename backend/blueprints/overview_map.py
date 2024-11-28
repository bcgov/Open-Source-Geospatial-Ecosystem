from flask import Blueprint, render_template
import os

# Get the path of `lup_overview.html`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(BASE_DIR, '..','templates','static', 'lup_overview.html')

# Blueprint setup
blueprint = Blueprint("Overview_Map", __name__,
                    static_folder='../templates/static',  
                    template_folder='../templates/templates')  

@blueprint.route("/overview_map")
def overview():
    # Read the HTML content of `lup_overview.html`
    with open(map_path, 'r') as f:
        leaflet_map = f.read()
    # Pass the content as a variable to `overview.html`
    return render_template("overview.html", leaflet_map=leaflet_map), 200
