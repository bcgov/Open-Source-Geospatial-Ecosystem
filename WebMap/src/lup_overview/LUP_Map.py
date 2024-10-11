import folium
import folium.elements
import geopandas
import feature_download
import os
from folium.utilities import JsCode
from folium.plugins import MarkerCluster
import folium.plugins as plugins
import branca.colormap as cm
import logging

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
    wfs_layer = wfs.get_data(layer, query=query, fields=fields, bbox=bbox)

    # Check if there is an active geometry column
    if wfs_layer.geometry.name is not None and not wfs_layer.geometry.empty:
        logging.info("Active geometry set")
    else:
        # Check for valid geometry columns and set it
        if 'GEOMETRY' in wfs_layer.columns:
            wfs_layer.set_geometry('GEOMETRY', inplace=True)
        elif 'SHAPE' in wfs_layer.columns:
            wfs_layer.set_geometry('SHAPE', inplace=True)
        else:
            logging.error("No valid geometry column found. Returning an empty GeoDataFrame.")
            return geopandas.GeoDataFrame()  # Return an empty GeoDataFrame if no geometry is found

    # Set the CRS and transform to WGS84
    wfs_layer = wfs_layer.set_crs('epsg:3005')
    wfs_layer = wfs_layer.to_crs(4326)
    
    return wfs_layer

# for center starting point
lon, lat= -128.867888, 55.781113
# for controlled extent 
min_lon, max_lon= -127.120663, -127.120663
min_lat, max_lat= 54.658317, 56.880993
zoom_start = 7
basemap='OpenStreetMap'


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
nass_WLA=wfs_getter('WHSE_LEGAL_ADMIN_BOUNDARIES.FNT_TREATY_AREA_SP', query="""TREATY = 'Nisga''a' and AREA_TYPE = 'Nass Wildlife Area'""")
nass_area=wfs_getter('WHSE_LEGAL_ADMIN_BOUNDARIES.FNT_TREATY_AREA_SP', query="""TREATY = 'Nisga''a' and AREA_TYPE = 'Nass Area'""")
min_pot=wfs_getter('WHSE_MINERAL_TENURE.MINPOT_MINERAL_POTENTIAL', bbox=bbox_albers)
# kalum_srmp= wfs_getter('WHSE_LAND_USE_PLANNING.RMP_STRGC_LAND_RSRCE_PLAN_SP', query="""STRGC_LAND_RSRCE_PLAN_ID=97""") # protected B layer, no WFS, need to find another way around
hanna_tintina=wfs_getter('WHSE_TANTALIS.TA_CONSERVANCY_AREAS_SVW', query=""" ADMIN_AREA_SID = 5420""")
# water_mgmt_non=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY',query="""NON_LEGAL_FEAT_OBJECTIVE = 'Water Management Units'""") # protected B layer, no WFS

#add wfs gdfs to foloium
folium.GeoJson(aoi,
            name='LUP AOI',
            style_function=lambda feature:{
                'fillColor':'transparent',
                'color':'black',
                'weight': 5
            }, ).add_to(m)

#set up marker clustering
rec_marker_cluster = MarkerCluster(name='Recreation Sites (Points)').add_to(m)
#set up pop up
rec_pop_point=folium.GeoJsonPopup(fields=rec_points[['PROJECT_NAME','FOREST_FILE_ID','MAINTAIN_STD_DESC','SITE_LOCATION', 'PROJECT_ESTABLISHED_DATE']].columns.tolist(), 
                        aliases=['Project Name', 'Forest File ID', 'Maintained Standard Description', 'Site Location','Established Date' ])
#set up layer
folium.GeoJson(rec_points, 
            name='Recreation Sites (Points)',
            highlight_function=lambda x: {'fillOpacity': 0.8},
            popup=rec_pop_point,
            zoom_on_click=True,).add_to(rec_marker_cluster)

rec_pop=folium.GeoJsonPopup(rec_polys[['PROJECT_NAME','FOREST_FILE_ID','SITE_LOCATION','PROJECT_TYPE', 'PROJECT_ESTABLISHED_DATE']].columns.tolist(),
                            aliases=['Project Name', 'Forest File ID','Site Location', 'Project Type','Established Date' ])
folium.GeoJson(rec_polys, 
            name='Recreation Sites (Polys)',
            style_function=lambda feature:{
                'fillColor':'transparent',
                'color':'#16de3d',
                'weight': 2
            }, 
            popup=rec_pop, 
                ).add_to(m)

cw_pop=folium.GeoJsonPopup(fields=com_watersheds[['CW_NAME','WATER_SYSTEM_NAME','CW_USE','CW_CODE','CW_DATE_CREATED','ORGANIZATION','POD_NUMBER','CW_LEGISLATION']].columns.tolist(),
                        aliases=['Community Watershed Name','Water System Name','Use','Community Watershed Code','CW Date Created','Organization','POD Number','Legislation'])
folium.GeoJson(com_watersheds,
            name='Community Watershed',
            style_function=lambda feature:{
                'fillColor':'#2c93af',
                'color':'#2c93af',
                'weight': 2
            }, 
            popup=cw_pop    
).add_to(m)

nass_wla_pop=folium.GeoJsonPopup(fields=nass_WLA[['TREATY_AREA_ID','TREATY','EFFECTIVE_DATE','FIRST_NATION_NAME','AREA_TYPE','CHAPTER_REFERENCE','APPENDIX_REFERENCE']].columns.tolist(),
                                aliases=['Treaty Area ID', 'Treaty', 'Effective Date', 'First Nation Name', 'Area Type', 'Chapter Reference', 'Appendix Reference'])
folium.GeoJson(nass_WLA,
            name= 'Nass Wildlife Area',
            style_function=lambda feature:{
                'fillColor':'#52c477',
                'color':'#3d8153',
                'weight': 2,
                'fillOpacity': 0.7,       
                'dashArray': '5, 5'         # Dotted outline
            },
            popup=nass_wla_pop).add_to(m)

nass_area_pop=folium.GeoJsonPopup(fields=nass_WLA[['TREATY_AREA_ID','TREATY','EFFECTIVE_DATE','FIRST_NATION_NAME','AREA_TYPE','CHAPTER_REFERENCE','APPENDIX_REFERENCE']].columns.tolist(),
                                aliases=['Treaty Area ID', 'Treaty', 'Effective Date', 'First Nation Name', 'Area Type', 'Chapter Reference', 'Appendix Reference'])
folium.GeoJson(nass_area,
            name='Nass Area',
            style_function=lambda feature:{
                'fillColor':'#b430e5',
                'color':'#570f71',
                'weight': 2,
                'fillOpacity': 0.7,       
                'dashArray': '5, 5'         # Dotted outline
            }, 
            popup=nass_area_pop
            ).add_to(m)

min_pot_pop=folium.GeoJsonPopup(fields=min_pot[['TRACT_ID','TRACT_POLYGON_AREA','NUMBER_OF_MINFILE_OCCURENCES','METALLIC_MINERAL_INVENTORY','RANK_OF_INDUSTRIAL_MINERALS']].columns.tolist(),
                                aliases=['Tract ID','Tract Polygon Area','Number Of Mine file Occurrences','Metallic Mineral Inventory','Rank Of Industrial Minerals'
])

#declare color ramp and set up stuff- would be nice to get color ramp legend tied to layer vis
min_pot_color=cm.linear.YlOrRd_04.scale(0, 800).to_step(100)
min_pot_color.caption = "Mineral Potential - Rank Of Industrial Minerals"
m.add_child(min_pot_color)

folium.GeoJson(min_pot,
            name='Mineral Potential',
            style_function=lambda feature:{
                'fillColor': min_pot_color(feature['properties']['RANK_OF_INDUSTRIAL_MINERALS']),
                'color':'#000000',
                'weight': 2,
                'fillOpacity': 0.7
                },
            popup=min_pot_pop).add_to(m)

#Manage tile layers
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('cartodb positron').add_to(m)
folium.TileLayer('Esri WorldImagery').add_to(m)
folium.TileLayer(show=True).add_to(m)
# add layer control 
folium.LayerControl().add_to(m)

#save html map
print(BASE_DIR)
m.save(os.path.join('LUP_Overview.html')) 