import folium
import folium.elements
import geopandas
import feature_download
import os
from folium.utilities import JsCode
import folium.plugins as plugins

# Load the local geojson AOI file and get bbox in Albers projection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
lup_aoi = os.path.join(BASE_DIR, '..','..', 'geojson', 'aoi.geojson')

#call feature downloader
wfs = feature_download.WFS_downloader()

#get bbox from aoi
aoi=geopandas.read_file(lup_aoi)
bbox_albers=wfs.create_bbox(aoi)
aoi=aoi.to_crs(4326)

def wfs_getter(layer, query=None, fields=None, bbox=None):
    wfs_layer=wfs.get_data(layer, query=query, bbox=bbox)
    wfs_layer=wfs_layer.set_crs('epsg:3005')
    wfs_layer=wfs_layer.to_crs(4326)
    return wfs_layer


# for center starting point
lon, lat= -128.867888, 55.781113
# for controlled extent 
min_lon, max_lon= -127.120663, -127.120663
min_lat, max_lat= 54.658317, 56.880993
zoom_start = 7
basemap="OpenStreetMap"


#call folium map object
m = folium.Map(
    max_bounds=False,
    location=[lat, lon],
    tiles=basemap,
    zoom_start=zoom_start,
    control_scale=True
)


#Call WFS
rec_points=wfs_getter('WHSE_FOREST_TENURE.FTEN_REC_SITE_POINTS_SVW', bbox=bbox_albers)
rec_polys=wfs_getter('WHSE_FOREST_TENURE.FTEN_RECREATION_POLY_SVW', bbox=bbox_albers)
com_watersheds=wfs_getter('WHSE_WATER_MANAGEMENT.WLS_COMMUNITY_WS_PUB_SVW', bbox=bbox_albers)

folium.GeoJson(aoi,
            name='LUP AOI',
            style_function=lambda feature:{
                "fillColor":"transparent",
                "color":"black",
                "weight": 5
            }, ).add_to(m)

rec_tt=folium.GeoJsonTooltip(fields=rec_points[['PROJECT_NAME','FOREST_FILE_ID','MAINTAIN_STD_DESC','SITE_LOCATION', 'PROJECT_ESTABLISHED_DATE']].columns.tolist(), 
                        aliases=['Project Name', 'Forest File ID', 'Maintained Standard Description', 'Site Location','Established Date' ])
folium.GeoJson(rec_points, 
            name='Recreation Sites (Points)',
            highlight_function=lambda x: {"fillOpacity": 0.8},
            tooltip=rec_tt,
            zoom_on_click=True,).add_to(m)

rec_pop=folium.GeoJsonPopup(rec_polys[['PROJECT_NAME','FOREST_FILE_ID','SITE_LOCATION','PROJECT_TYPE', 'PROJECT_ESTABLISHED_DATE']].columns.tolist(),
                            aliases=['Project Name', 'Forest File ID','Site Location', 'Project Type','Established Date' ])
folium.GeoJson(rec_polys, 
            name='Recreation Sites (Polys)',
            style_function=lambda feature:{
                "fillColor":"transparent",
                "color":"green",
                "weight": 2
            }, 
            popup=rec_pop 
                ).add_to(m)

cw_pop=folium.GeoJsonPopup(fields=com_watersheds[['CW_NAME','WATER_SYSTEM_NAME','CW_USE','CW_CODE','CW_DATE_CREATED','ORGANIZATION','POD_NUMBER','CW_LEGISLATION']].columns.tolist(),
                        aliases=['Community Watershed Name','Water System Name','Use','Community Watershed Code','CW Date Created','Organization','POD Number','Legislation'])
folium.GeoJson(com_watersheds,
            name='Community Watershed',
            style_function=lambda feature:{
                "fillColor":"light blue",
                "color":"blue",
                "weight": 2
            }, 
            popup=cw_pop    
).add_to(m)


#Manage tile layers
folium.TileLayer("OpenStreetMap").add_to(m)
folium.TileLayer("cartodb positron").add_to(m)
folium.TileLayer("Esri WorldImagery").add_to(m)
folium.TileLayer(show=True).add_to(m)
# add layer control 
folium.LayerControl().add_to(m)

#save html map
print(BASE_DIR)
m.save(os.path.join('LUP_Overview.html')) 