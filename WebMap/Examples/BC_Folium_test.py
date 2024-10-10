import folium
import sys

import folium.raster_layers
from folium import raster_layers
import feature_download

import rasterio
from rasterio.plot import reshape_as_image
import numpy as np 
import matplotlib.pyplot as plt
from io import BytesIO 


wfs = feature_download.WFS_downloader()

# for center starting point
lon, lat= -122.820, 58.420
# for controlled extent 
min_lon, max_lon= -119.586182, -125
min_lat, max_lat= 55.807456, 60.462634
zoom_start = 7
basemap="OpenStreetMap"

bbox = "-125,55.8,-119.586182,60.462634"

#call folium map object
m = folium.Map(
    max_bounds=True,
    location=[lat, lon],
    tiles=basemap,
    zoom_start=zoom_start,
    control_scale=True,   
    min_lat=min_lat,
    max_lat=max_lat,
    min_lon=min_lon,
    max_lon=max_lon,
)

#Add WMS layers
water_bodies=folium.WmsTileLayer(
    url='https://openmaps.gov.bc.ca/geo/pub/WHSE_BASEMAPPING.TRIM_EBM_WATERBODIES/ows',
    name= 'Waterbodies - TRIM Enhanced Base Map (EBM)',
    fmt='image/png',
    layers='pub:WHSE_BASEMAPPING.TRIM_EBM_WATERBODIES',
    transparent=True, 
    overlay=True,
    control=True,
    show=True
)
water_bodies.add_to(m)

nat_dist=folium.WmsTileLayer(
    url='https://openmaps.gov.bc.ca/geo/pub/WHSE_FOREST_VEGETATION.BEC_NATURAL_DISTURBANCE_SV/ows',
    name= 'Natural Disturbance Type',
    fmt='image/png',
    layers='pub:WHSE_FOREST_VEGETATION.BEC_NATURAL_DISTURBANCE_SV',
    transparent=True, 
    overlay=True,
    control=True,
    show=True
)
nat_dist.add_to(m)

bs=folium.WmsTileLayer(
    url='https://openmaps.gov.bc.ca/geo/pub/WHSE_FOREST_VEGETATION.VEG_BURN_SEVERITY_SAME_YR_SP/ows',
    name='Fire Burn Severity - Same Year',
    fmt='image/png',
    layers='pub:WHSE_FOREST_VEGETATION.VEG_BURN_SEVERITY_SAME_YR_SP',
    transparent=True,
    overlay=True,
    control=True,
    show=True
)
bs.add_to(m)

# curr_fire_per=folium.WmsTileLayer(
#     url='https://openmaps.gov.bc.ca/geo/pub/WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP/ows',
#     name='BC Wildfire Fire Perimeters - Current',
#     fmt='image/png',
#     layers='pub:WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP',
#     transparent=True, 
#     overlay=True,
#     control=True,
#     show=True
# )
# curr_fire_per.add_to(m)


#wms legend, have to create with html and add I think geojson legends would work
legend_html = """
<div style="
position: fixed; 
bottom: 60px; left: 50px; width: 200px; height: 165px; 
border:2px solid grey; z-index:9999; font-size:14px;
background-color:white;
">

&nbsp; <i style="background: #ffffff; width: 12px; height: 12px; display: inline-block; border: 2px solid #e31a1c; box-sizing: border-box;"></i>&nbsp; Current Wildfire Perimeters <br>
<br>
&nbsp; <b>Burn Severity </b> <br>
&nbsp; <i style="background: #d1ff73; width: 12px; height: 12px; display: inline-block;"></i>&nbsp; Unburned <br>
&nbsp; <i style="background: #ffff73; width: 12px; height: 12px; display: inline-block;"></i>&nbsp; Low <br>
&nbsp; <i style="background: #ffd37f; width: 12px; height: 12px; display: inline-block;"></i>&nbsp; Moderate <br>
&nbsp; <i style="background: #ff7f7f; width: 12px; height: 12px; display: inline-block;"></i>&nbsp; High <br>
</div>
"""
#add legend to map
m.get_root().html.add_child(folium.Element(legend_html))



# GeoJSONs

# fire perimeters from geopandas and bcgw WFS
current_perimeters=wfs.get_data(dataset='WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP', query= """FIRE_NUMBER LIKE 'G9%' """)
current_perimeters=current_perimeters.set_crs('epsg:3005')
current_perimeters=current_perimeters.to_crs(4326)

pop=folium.GeoJsonPopup(current_perimeters[['FIRE_NUMBER','FIRE_YEAR','FIRE_SIZE_HECTARES','LOAD_DATE','FIRE_STATUS','FIRE_URL']].columns.tolist())
tip=folium.GeoJsonTooltip(['FIRE_NUMBER','FIRE_YEAR','FIRE_SIZE_HECTARES','LOAD_DATE','FIRE_STATUS','FIRE_URL'])

folium.GeoJson(current_perimeters, 
            name='Current Wildfires (G9)',
            style_function=lambda feature:{
                "fillColor":"transparent",
                "color":"Red",
                "weight": 2
            }, 
            popup=pop, 
            tooltip=tip
                ).add_to(m)


#local geojson
#popup for geojson
popup = folium.GeoJsonPopup(fields=["Range"])
tooltip = folium.GeoJsonTooltip(fields=["Range"])
#add local geojson 
folium.GeoJson(
    'Folium/Herds.geojson',
    zoom_on_click=True,
    style_function=lambda feature: {
        "fillColor": "purple",
        "color": "black",
        "weight":2
    },
        highlight_function=lambda feature: {
        "fillColor":'yellow'
    },
    name='Herds',
    popup=popup,
    tooltip=tooltip,
    popup_keep_highlighted=True,
    ).add_to(m)


# #import raster
print('start raster process')
dem=r'bcalbers/94p-albers-hillshd-bw-315.tif'

#open raster
dem_open=rasterio.open(dem)
dem_array=dem_open.read(1)

boundslist=[x for x in dem_open.bounds]

# #drop NAN values 
dem_array=np.nan_to_num(dem_array)

print('folium raster call ')
# # Use Folium ImageOverlay to add the image to the map gets hung up here?
f_dem=raster_layers.ImageOverlay(
    image=dem_array,
    bounds=[[boundslist[1], boundslist[0]], [boundslist[3], boundslist[2]]],
    opacity=0.6,
    interactive=True,
    cross_origin=False,
    name= '94p DEM',)
f_dem.add_to(m)


#Manage tile layers
folium.TileLayer("OpenStreetMap").add_to(m)
folium.TileLayer("cartodb positron").add_to(m)
folium.TileLayer("Esri WorldImagery").add_to(m)
folium.TileLayer(show=True).add_to(m)

folium.LayerControl().add_to(m)

#add circle markers to max extents
# folium.CircleMarker([max_lat, min_lon], tooltip="Upper Left Corner").add_to(m)
# folium.CircleMarker([min_lat, min_lon], tooltip="Lower Left Corner").add_to(m)
# folium.CircleMarker([min_lat, max_lon], tooltip="Lower Right Corner").add_to(m)
# folium.CircleMarker([max_lat, max_lon], tooltip="Upper Right Corner").add_to(m)

#save map 
m.save('test_map.html')

# add legend for NDT TYPE
#add time wms for historic perimeters and severity? maybe linked on one slider?
#find bc public geojsons? or how to leverage rest server #
#https://dev.to/chinazoanebelundu/plotting-interactive-map-in-python-using-folium-beginner-friendly-6ni


#add clustering of fire polygons https://python-visualization.github.io/folium/latest/reference.html#folium.plugins.MarkerCluster
#might have to make an array of centroids then specify when they disapear?

# can add form wfs and geopandas done, now do more


# https://andrewpwheeler.com/2023/04/25/hacking-folium-for-nicer-legends/