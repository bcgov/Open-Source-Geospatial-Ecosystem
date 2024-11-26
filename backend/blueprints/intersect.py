from flask import Blueprint, render_template, request, jsonify, Response
import requests
from shapely.geometry import shape
import geojson
import geopandas as gpd
import io
import os

blueprint = Blueprint('intersect',__name__,
                    static_folder='./templates/static',  
                    template_folder='./templates/templates')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(BASE_DIR, '..','templates','static', 'lup_intersect.html')

# Define bounding box
bba = (743161, 1112127, 898012, 1291756, 'urn:ogc:def:crs:EPSG:3005')
#input intersect layers
legal_poly="WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW"
legal_line="WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_LINE_SVW"
legal_point="WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POINT_SVW"
non_poly="WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW"
non_line="WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_LINE_SVW"
non_point="WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POINT_SVW"

def wfs_query_to_gdf(dataset, query=None, fields=None, bbox=None, offset=0, max_features=10000):
    """Fetch data from a WFS endpoint and return it as a GeoDataFrame, handling pagination."""
    if fields is None:
        fields = []

    url = r"https://openmaps.gov.bc.ca/geo/pub/ows?"
    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'GetFeature',
        'typeName': f'pub:{dataset}',
        'outputFormat': 'application/json',
        "srsName": "EPSG:3005",
        'sortBy': 'OBJECTID',
        'startIndex': offset,
        'maxFeatures': max_features  # Adjust as needed
    }

    if bbox is not None and query is not None:
        bbox_str = f"BBOX(GEOMETRY,{','.join(map(str, bbox))}, 'urn:ogc:def:crs:EPSG:3005')"
        query = f"{bbox_str} AND {query}"
    elif bbox is not None:
        bbox_str = f"{','.join(map(str, bbox))}"
        params['bbox'] = bbox_str
    if query is not None:
        params['CQL_FILTER'] = query
    if fields:
        params['propertyName'] = ','.join(fields).upper()

    all_features = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise RuntimeError(f"Error fetching WFS data: {response.status_code} - {response.text}")

        # Load GeoJSON data using geojson library for easier manipulation
        geojson_data = geojson.loads(response.text)  # Load JSON into GeoJSON format
        
        # Add features to the list
        all_features.extend(geojson_data["features"])

        # If fewer features than requested, we are done
        if len(geojson_data["features"]) < max_features:
            break

        # Update the offset for the next page
        offset += max_features
        params['startIndex'] = offset

    # Handle case if no features were returned
    if not all_features:
        return None  # Return None instead of empty GeoDataFrame

    # Convert the accumulated features to a GeoDataFrame using geopandas
    gdf = gpd.GeoDataFrame.from_features(all_features, crs="EPSG:3005")
    return gdf


def intersect_with_wfs(uploaded_gdf, gdf_from_wfs):
    if gdf_from_wfs is None or len(gdf_from_wfs) == 0:
        return None  # Return None if no data from WFS

    # Ensure both GeoDataFrames have the same CRS
    if uploaded_gdf.crs != gdf_from_wfs.crs:
        gdf_from_wfs = gdf_from_wfs.to_crs(uploaded_gdf.crs)

    # Perform intersection
    # intersected_data = gpd.overlay(uploaded_gdf, gdf_from_wfs, how='intersection')
    intersected_data = gpd.sjoin(gdf_from_wfs, uploaded_gdf, how='inner', predicate='intersects')
    
    if intersected_data.empty:
        return None

    # Convert Timestamp columns to string before serializing to JSON
    for column in intersected_data.select_dtypes(include=['datetime']).columns:
        intersected_data[column] = intersected_data[column].astype(str)

    # Return the GeoDataFrame (not the JSON string)
    return intersected_data

def process_wfs_intersection(user_data, dataset, columns, bbox):
    gdf = wfs_query_to_gdf(dataset=dataset, bbox=bbox)
    if gdf is not None:
        intersected = intersect_with_wfs(user_data, gdf)
        if intersected is not None:
            return gdf, intersected[columns].to_dict(orient='records')
    return None, None

def legal_data_intersect(user_data):
    legal_columns = [
        'LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE',
        'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 
        'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK'
    ]
    # Process intersections for polygons, lines, and points
    legal_polys_gdf, intersected_legal_poly_list = process_wfs_intersection(
        user_data, legal_poly, legal_columns, bba
    )
    legal_lines_gdf, intersected_legal_line_list = process_wfs_intersection(
        user_data, legal_line, legal_columns, bba
    )
    legal_points_gdf, intersected_legal_point_list = process_wfs_intersection(
        user_data, legal_point, legal_columns, bba
    )
    
    return (
        legal_polys_gdf, intersected_legal_poly_list, 
        legal_lines_gdf, intersected_legal_line_list, 
        legal_points_gdf, intersected_legal_point_list
    )
    
def non_legal_data_intersect(user_data):
    non_columns = [
        'NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME',
        'NON_LEGAL_FEAT_OBJECTIVE', 'ORIGINAL_DECISION_DATE'
    ]

    non_polys_gdf, intersected_non_legal_poly_list = process_wfs_intersection(
        user_data, non_poly, non_columns, bba
    )
    non_lines_gdf, intersected_non_legal_line_list = process_wfs_intersection(
        user_data, non_line, non_columns, bba
    )
    non_points_gdf, intersected_non_legal_point_list = process_wfs_intersection(
        user_data, non_point, non_columns, bba
    )
    
    return (
        non_polys_gdf, intersected_non_legal_poly_list, 
        non_lines_gdf, intersected_non_legal_line_list, 
        non_points_gdf, intersected_non_legal_point_list
    )

legal_polys_gdf = None
legal_lines_gdf = None
legal_points_gdf = None
non_polys_gdf = None
non_lines_gdf = None
non_points_gdf = None


@blueprint.route('/intersect', methods=['GET', 'POST'])
def intersect():
    global legal_polys_gdf, legal_lines_gdf, legal_points_gdf, non_polys_gdf, non_lines_gdf, non_points_gdf
    with open(map_path, 'r') as f:
        leaflet_map = f.read()
    if request.method == 'POST':
        # Step 1: Read the uploaded file
        uploaded_file = request.files['file']
        data_type = request.form['data_type']
        uploaded_gdf = None

        if uploaded_file.filename.endswith('.geojson'):
            uploaded_gdf = gpd.read_file(uploaded_file)
        elif uploaded_file.filename.endswith('.shp'):
            uploaded_gdf = gpd.read_file(uploaded_file)
        elif uploaded_file.filename.endswith('.kml'):
            uploaded_gdf = gpd.read_file(uploaded_file)
        elif uploaded_file.filename.endswith('.gpx'):
            uploaded_gdf = gpd.read_file(uploaded_file)

        if uploaded_gdf is not None:
            
            intersected_data_1 = None
            intersected_data_2 = None
            intersected_data_3 = None
            intersected_data_4 = None
            intersected_data_5 = None
            intersected_data_6 = None
            
            if data_type == 'legal':
                legal_polys_gdf, intersected_legal_poly_list, \
                legal_lines_gdf, intersected_legal_line_list, \
                legal_points_gdf, intersected_legal_point_list = legal_data_intersect(uploaded_gdf)
                
                intersected_data_1=intersected_legal_poly_list
                intersected_data_2=intersected_legal_line_list
                intersected_data_3=intersected_legal_point_list
                intersected_data_4=None
                intersected_data_5=None
                intersected_data_6=None
                
                legal_polys_gdf = legal_polys_gdf
                legal_lines_gdf = legal_lines_gdf
                legal_points_gdf = legal_points_gdf

                
            elif data_type =='non_legal':    
                non_polys_gdf, intersected_non_legal_poly_list, \
                non_lines_gdf, intersected_non_legal_line_list, \
                non_points_gdf, intersected_non_legal_point_list = non_legal_data_intersect(uploaded_gdf)
                
                intersected_data_1=None
                intersected_data_2=None
                intersected_data_3=None
                intersected_data_4=intersected_non_legal_poly_list
                intersected_data_5=intersected_non_legal_line_list
                intersected_data_6=intersected_non_legal_point_list
                
                non_polys_gdf = non_polys_gdf
                non_lines_gdf = non_lines_gdf
                non_points_gdf = non_points_gdf
                
                
            elif data_type =='both':
                legal_polys_gdf, intersected_legal_poly_list, \
                legal_lines_gdf, intersected_legal_line_list, \
                legal_points_gdf, intersected_legal_point_list = legal_data_intersect(uploaded_gdf)
                
                intersected_data_1=intersected_legal_poly_list
                intersected_data_2=intersected_legal_line_list
                intersected_data_3=intersected_legal_point_list
                
                non_polys_gdf, intersected_non_legal_poly_list, \
                non_lines_gdf, intersected_non_legal_line_list, \
                non_points_gdf, intersected_non_legal_point_list = non_legal_data_intersect(uploaded_gdf)             
                
                intersected_data_4=intersected_non_legal_poly_list
                intersected_data_5=intersected_non_legal_line_list
                intersected_data_6=intersected_non_legal_point_list
                
                legal_polys_gdf = legal_polys_gdf
                legal_lines_gdf = legal_lines_gdf
                legal_points_gdf = legal_points_gdf
                non_polys_gdf = non_polys_gdf
                non_lines_gdf = non_lines_gdf
                non_points_gdf = non_points_gdf
            
                
            return render_template(
                'intersect.html',
                leaflet_map=leaflet_map,
                intersected_data_1=intersected_data_1,
                intersected_data_2=intersected_data_2,
                intersected_data_3=intersected_data_3,
                intersected_data_4=intersected_data_4,
                intersected_data_5=intersected_data_5,
                intersected_data_6=intersected_data_6,
            )
    # For GET requests, set default values for the data variables
    return render_template(
        'intersect.html',
        leaflet_map=leaflet_map,
        intersected_data_1=None,
        intersected_data_2=None,
        intersected_data_3=None,
        intersected_data_4=None,
        intersected_data_5=None,
        intersected_data_6=None
    )
    
@blueprint.route('/get_gdfs', methods=['GET'])
def get_gdfs():
    """Return GeoJSON representations of legal and non-legal polygons."""
    try:
        gdfs = {
            "legal_polys": legal_polys_gdf.to_json() if legal_polys_gdf is not None else None,
            "legal_lines": legal_lines_gdf.to_json() if legal_lines_gdf is not None else None,
            "legal_points": legal_points_gdf.to_json() if legal_points_gdf is not None else None,
            "non_legal_polys": non_polys_gdf.to_json() if non_polys_gdf is not None else None,
            "non_legal_lines": non_lines_gdf.to_json() if non_lines_gdf is not None else None,
            "non_legal_points": non_points_gdf.to_json() if non_points_gdf is not None else None,
        }
        # Remove any None entries
        gdfs = {key: value for key, value in gdfs.items() if value is not None}
        return jsonify(gdfs)
    except Exception as e:
        blueprint.logger.error(f"Error in /get_gdfs: {e}")
        return jsonify({"error": str(e)}), 500