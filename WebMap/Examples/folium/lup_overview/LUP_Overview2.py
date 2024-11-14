import folium
import folium.elements
import geopandas
import feature_download
import os
from folium.utilities import JsCode
from folium.plugins import MarkerCluster, GroupedLayerControl
import folium.plugins as plugins
import branca.colormap as cm
import logging
import gc
import topojson as tp
import shapely.wkt
import json 
from folium_glify_layer import GlifyLayer, Popup, Tooltip
import re 
import gzip
# Load the local geojson AOI file and get bbox in Albers projection
BASE_DIR = os.getcwd()
lup_aoi = os.path.join(BASE_DIR, 'WebMap','geojson', 'aoi.geojson')




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
    prefer_canvas=True,
    tiles=basemap,
    zoom_start=zoom_start,
    control_scale=True
)

#add stripes plugin in
stripes_45 = folium.plugins.pattern.StripePattern(angle=-45).add_to(m)
stripes_135=folium.plugins.pattern.StripePattern(angle=-135).add_to(m)


dfs=[]
df_names=[]

spec_hab = wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Special Habitats for General Wildlife'""",fields=['STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers) 
dfs.append(spec_hab)
df_names.append('spec_hab')

water_mgmt=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW',query="""LEGAL_FEAT_OBJECTIVE = 'Water Management Units'""", fields=['STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(water_mgmt)
df_names.append('water_mgmt')

legal_g_hawk_nesting= wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Goshawk Nesting/Post-Fledging Habitat' And STRGC_LAND_RSRCE_PLAN_NAME IN ('Cranberry Sustainable Resource Management Plan', 'Nass South Sustainable Resource Management Plan')""", fields=['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(legal_g_hawk_nesting)
df_names.append('legal_g_hawk_nesting')

non_legal_g_hawk_nesting= wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW', query="""NON_LEGAL_FEAT_OBJECTIVE = 'Goshawk Nesting/Post-Fledging Habitat' And STRGC_LAND_RSRCE_PLAN_NAME IN ('Cranberry Sustainable Resource Management Plan', 'Nass South Sustainable Resource Management Plan')""", fields=['NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME','NON_LEGAL_FEAT_OBJECTIVE','ORIGINAL_DECISION_DATE','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(non_legal_g_hawk_nesting)
df_names.append('non_legal_g_hawk_nesting')

rmp_nonlegal_moose=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW', query="""NON_LEGAL_FEAT_OBJECTIVE = 'Moose Winter Range'  """, fields=['NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME','NON_LEGAL_FEAT_OBJECTIVE','ORIGINAL_DECISION_DATE','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(rmp_nonlegal_moose)
df_names.append('rmp_nonlegal_moose')

rmp_legal_moose=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Moose Winter Range'  """, fields=['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(rmp_legal_moose)
df_names.append('rmp_legal_moose')


eca_threshold=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Equivalent Clearcut Area Threshold Watersheds'""", fields=['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(eca_threshold)
df_names.append('eca_threshold')

ecosystem_net=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Ecosystem Network'""", fields=['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(ecosystem_net)
df_names.append('ecosystem_net')

ecosystem_buf=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW', query="""NON_LEGAL_FEAT_OBJECTIVE = 'Ecosystem Network Buffer'""", fields=['NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME','NON_LEGAL_FEAT_OBJECTIVE','ORIGINAL_DECISION_DATE','GEOMETRY','OBJECTID'])
dfs.append(ecosystem_buf)
df_names.append('ecosystem_buf')

cedar_reserves=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Cedar Stand Reserves'""", fields=['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(cedar_reserves)
df_names.append('cedar_reserves')

gc.collect()

griz_wtrshd=wfs_getter('WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW', query="""LEGAL_FEAT_OBJECTIVE = 'Cedar Stand Reserves'""", fields=['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(griz_wtrshd)
df_names.append('griz_wtrshd')
#Call WFS
rec_points=wfs_getter('WHSE_FOREST_TENURE.FTEN_REC_SITE_POINTS_SVW', fields=['PROJECT_NAME','FOREST_FILE_ID','MAINTAIN_STD_DESC','SITE_LOCATION', 'PROJECT_ESTABLISHED_DATE','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(rec_points)
df_names.append('rec_points')

rec_polys=wfs_getter('WHSE_FOREST_TENURE.FTEN_RECREATION_POLY_SVW', fields=['PROJECT_NAME','FOREST_FILE_ID','SITE_LOCATION','PROJECT_TYPE', 'PROJECT_ESTABLISHED_DATE','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(rec_polys)
df_names.append('rec_polys')

com_watersheds=wfs_getter('WHSE_WATER_MANAGEMENT.WLS_COMMUNITY_WS_PUB_SVW',fields=['CW_NAME','WATER_SYSTEM_NAME','CW_USE','CW_CODE','CW_DATE_CREATED','ORGANIZATION','POD_NUMBER','CW_LEGISLATION','SHAPE','OBJECTID'], bbox=bbox_albers)
dfs.append(com_watersheds)
df_names.append('com_watersheds')


parcel_fabric = wfs_getter('WHSE_CADASTRE.PMBC_PARCEL_FABRIC_POLY_SVW', fields=['PARCEL_NAME', 'OWNER_TYPE','SHAPE','OBJECTID'], bbox=bbox_albers ) #query="""OWNER_TYPE='Private'"""  

private_parcels = parcel_fabric[parcel_fabric['OWNER_TYPE'] == 'Private']
dfs.append(private_parcels)
df_names.append('private_parcels')

gc.collect()

uwr_mountain_goat = wfs_getter('WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP', query="""SPECIES_1 = 'M-ORAM' Or SPECIES_2 = 'M-ORAM'""", fields=['SPECIES_1', 'SPECIES_2','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(uwr_mountain_goat)
df_names.append('uwr_mountain_goat')

legal_ogmas = wfs_getter('WHSE_LAND_USE_PLANNING.RMP_OGMA_LEGAL_CURRENT_SVW', fields=['LEGAL_OGMA_PROVID', 'OGMA_TYPE', 'OGMA_PRIMARY_REASON', 'LEGALIZATION_FRPA_DATE', 'LEGALIZATION_OGAA_DATE', 'ASSOCIATED_ACT_NAME','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(legal_ogmas)
df_names.append('legal_ogmas')

nass_WLA=wfs_getter('WHSE_LEGAL_ADMIN_BOUNDARIES.FNT_TREATY_AREA_SP', query="""TREATY = 'Nisga''a' and AREA_TYPE = 'Nass Wildlife Area'""", fields=['TREATY_AREA_ID','TREATY','EFFECTIVE_DATE','FIRST_NATION_NAME','AREA_TYPE','CHAPTER_REFERENCE','APPENDIX_REFERENCE','GEOMETRY','OBJECTID'])
dfs.append(nass_WLA)
df_names.append('nass_WLA')

nass_area=wfs_getter('WHSE_LEGAL_ADMIN_BOUNDARIES.FNT_TREATY_AREA_SP', query="""TREATY = 'Nisga''a' and AREA_TYPE = 'Nass Area'""", fields=['TREATY_AREA_ID','TREATY','EFFECTIVE_DATE','FIRST_NATION_NAME','AREA_TYPE','CHAPTER_REFERENCE','APPENDIX_REFERENCE','GEOMETRY','OBJECTID'])
dfs.append(nass_area)
df_names.append('nass_area')

min_pot=wfs_getter('WHSE_MINERAL_TENURE.MINPOT_MINERAL_POTENTIAL', fields=['TRACT_ID','TRACT_POLYGON_AREA','NUMBER_OF_MINFILE_OCCURENCES','METALLIC_MINERAL_INVENTORY','RANK_OF_INDUSTRIAL_MINERALS','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(min_pot)
df_names.append('min_pot')

kalum_srmp= wfs_getter('WHSE_LAND_USE_PLANNING.RMP_STRGC_LAND_RSRCE_PLAN_SVW', query="""STRGC_LAND_RSRCE_PLAN_ID=149""", fields=['STRGC_LAND_RSRCE_PLAN_ID','STRGC_LAND_RSRCE_PLAN_NAME','PLAN_TYPE','PLAN_STATUS','APPROVAL_DATE','APPROVAL_LAST_AMEND_DATE','LEGALIZATION_DATE','LEGALIZATION_LAST_AMEND_DATE','GEOMETRY','OBJECTID'])
dfs.append(kalum_srmp)
df_names.append('kalum_srmp')

kalum_lrmp= wfs_getter('WHSE_LAND_USE_PLANNING.RMP_STRGC_LAND_RSRCE_PLAN_SVW', query="""STRGC_LAND_RSRCE_PLAN_ID=20""", fields=['STRGC_LAND_RSRCE_PLAN_ID','STRGC_LAND_RSRCE_PLAN_NAME','PLAN_TYPE','PLAN_STATUS','APPROVAL_DATE','APPROVAL_LAST_AMEND_DATE','LEGALIZATION_DATE','LEGALIZATION_LAST_AMEND_DATE','GEOMETRY','OBJECTID'])
dfs.append(kalum_lrmp)
df_names.append('kalum_lrmp')

gc.collect()

cranberry_srmp= wfs_getter('WHSE_LAND_USE_PLANNING.RMP_STRGC_LAND_RSRCE_PLAN_SVW', query="""STRGC_LAND_RSRCE_PLAN_ID=151""", fields=['STRGC_LAND_RSRCE_PLAN_ID','STRGC_LAND_RSRCE_PLAN_NAME','PLAN_TYPE','PLAN_STATUS','APPROVAL_DATE','APPROVAL_LAST_AMEND_DATE','LEGALIZATION_DATE','LEGALIZATION_LAST_AMEND_DATE','GEOMETRY','OBJECTID'])
dfs.append(cranberry_srmp)
df_names.append('cranberry_srmp')


hanna_tintina=wfs_getter('WHSE_TANTALIS.TA_CONSERVANCY_AREAS_SVW', query=""" ADMIN_AREA_SID = 5420""", fields=['ADMIN_AREA_SID','CONSERVANCY_AREA_NAME','ORCS_PRIMARY','ORCS_SECONDARY','ESTABLISHMENT_DATE','OFFICIAL_AREA_HA','PARK_MANAGEMENT_PLAN_URL','SHAPE','OBJECTID'])
dfs.append(hanna_tintina)
df_names.append('hanna_tintina')

visual_landscape_inventory = wfs_getter('WHSE_FOREST_VEGETATION.REC_VISUAL_LANDSCAPE_INVENTORY', query="""REC_EVC_FINAL_VALUE_CODE IS NOT NULL""", fields=['PROJECT_NAME','REC_EVC_FINAL_VALUE_CODE', 'REC_EVQO_CODE','RATIONALE','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(visual_landscape_inventory)
df_names.append('visual_landscape_inventory')

uwr_moose=wfs_getter('WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP', query="""SPECIES_1 IN ('M-ALAL', 'M-ALAL;M-CEEL;M-ODHE;M-ODVI') Or SPECIES_2 IN ('M-ALAL', 'M-ODHE; M-ALAL')""", fields=['SPECIES_1', 'SPECIES_2','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(uwr_moose)
df_names.append('uwr_moose')


aquired_tenures_hist=wfs_getter('WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_HISTORY_SP',fields=['TENURE_HISTORY_ID', 'TENURE_NUMBER_ID','TENURE_TYPE_DESCRIPTION','REVISION_NUMBER','GEOMETRY','OBJECTID'],bbox=bbox_albers)
aquired_tenures_hist['geometry']=aquired_tenures_hist['geometry'].simplify(tolerance=0.01)

aquired_tenures_curr=wfs_getter('WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW', fields=['TENURE_NUMBER_ID', 'CLAIM_NAME','TENURE_TYPE_DESCRIPTION','TENURE_SUB_TYPE_DESCRIPTION','TITLE_TYPE_DESCRIPTION','ISSUE_DATE','GOOD_TO_DATE','AREA_IN_HECTARES','REVISION_NUMBER','GEOMETRY','OBJECTID'] ,bbox=bbox_albers)
dfs.append(aquired_tenures_curr)
df_names.append('aquired_tenures_curr')

wha_grizzly= wfs_getter('WHSE_WILDLIFE_MANAGEMENT.WCP_WILDLIFE_HABITAT_AREA_POLY', query="""COMMON_SPECIES_NAME = 'Grizzly Bear'""", fields=['HABITAT_AREA_ID', 'TAG','APPROVAL_DATE','FEATURE_NOTES','COMMON_SPECIES_NAME','LEGISLATION_ACT_NAME','TIMBER_HARVEST_CODE','HECTARES','GEOMETRY','OBJECTID'], bbox=bbox_albers)
dfs.append(wha_grizzly)
df_names.append('wha_grizzly')



parks_reserves_protected_areas=wfs_getter('WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW', fields=['ADMIN_AREA_SID','PROTECTED_LANDS_NAME','PROTECTED_LANDS_DESIGNATION','PARK_CLASS','OFFICIAL_AREA_HA','PARK_MANAGEMENT_PLAN_URL','SHAPE','OBJECTID'], bbox=bbox_albers)
dfs.append(parks_reserves_protected_areas)
df_names.append('parks_reserves_protected_areas')

bec= wfs_getter('WHSE_FOREST_VEGETATION.BEC_BIOGEOCLIMATIC_POLY',fields=['MAP_LABEL','ZONE','SUBZONE','VARIANT','PHASE','NATURAL_DISTURBANCE','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(bec)
df_names.append('bec')

ecosections=wfs_getter('WHSE_TERRESTRIAL_ECOLOGY.ERC_ECOSECTIONS_SP',fields=['ECOSECTION_CODE','ECOSECTION_NAME','EFFECTIVE_DATE','EXPIRY_DATE','GEOMETRY','OBJECTID'],bbox=bbox_albers)
dfs.append(ecosections)
df_names.append('ecosections')

fn_reserves_crown_ten= wfs_getter('WHSE_TANTALIS.TA_CROWN_TENURES_SVW', query="""TENURE_TYPE = 'RESERVE/NOTATION'""", fields=['INTRID_SID','TENURE_STAGE','TENURE_STATUS','TENURE_TYPE','TENURE_SUBTYPE','TENURE_PURPOSE','CROWN_LANDS_FILE','TENURE_EXPIRY','TENURE_LEGAL_DESCRIPTION','TENURE_AREA_IN_HECTARES','SHAPE','OBJECTID'])


minx, miny, maxx, maxy = aoi.total_bounds

#reduces size of this layer but not by enough
fn_reserves_crown_ten=fn_reserves_crown_ten.cx[minx:maxx, miny:maxy]

print(len(fn_reserves_crown_ten))
size_in_memory = fn_reserves_crown_ten.memory_usage(deep=True).sum()
size_kb = size_in_memory / 1024  # Corrected: use parentheses for a float
print(size_kb)
dfs.append(fn_reserves_crown_ten)
df_names.append('fn_reserves_crown_ten')

#change precision of geom 4 decimal places should still be meter percision 
for df in dfs:
    try:
        # Use .loc to modify the geometry column safely and check if column exists
        if 'geometry' in df.columns:
            df.loc[:, 'geometry'] = df['geometry'].apply(
                lambda geom: geom if geom is None else shapely.wkt.loads(shapely.wkt.dumps(geom, rounding_precision=4))
            )
        elif 'shape' in df.columns:
            df.loc[:, 'shape'] = df['shape'].apply(
                lambda geom: geom if geom is None else shapely.wkt.loads(shapely.wkt.dumps(geom, rounding_precision=4))
            )
    except Exception as e:
        print(f"Error processing DataFrame: {e}")

#check data for layers with more than 1000 features or that are larger than 1000kb
big_data = []
big_data_names=[]
for name, d in zip(df_names, dfs):
    df_len = len(d)
    size_in_memory = d.memory_usage(deep=True).sum()
    size_kb = size_in_memory / 1024  # Corrected: use parentheses for a float

    if df_len > 1000 or size_kb > 1000:
        print(f"{name}: {df_len} features, GeoDataFrame memory usage: {size_kb:.2f} KB")  # Format size_kb to 2 decimal places
        big_data.append(d)
        big_data_names.append(name)
print(f"{len(big_data)} dfs over 1000 features or over 1000kb")


gc.collect()

for name,df in zip(big_data_names,big_data):
    
    name=df.to_json()
    name = json.loads(df.to_json())
    
#add wfs gdfs to foloium
folium.GeoJson(aoi,
            name='LUP AOI',
            style_function=lambda feature:{
                'fillColor':'transparent',
                'color':'black',
                'weight': 5
            },
            show=True
            ).add_to(m)

#set up marker clustering
rec_marker_cluster = MarkerCluster(name='Recreation Sites (Points)').add_to(m)
#set up pop up
rec_pop_point=folium.GeoJsonPopup(fields=rec_points[['PROJECT_NAME','FOREST_FILE_ID','MAINTAIN_STD_DESC','SITE_LOCATION', 'PROJECT_ESTABLISHED_DATE']].columns.tolist(), 
                        aliases=['Project Name', 'Forest File ID', 'Maintained Standard Description', 'Site Location','Established Date' ])
#set up layer
#because rec points get added to the maker cluster show needs to = True, which is the default 
folium.GeoJson(rec_points, 
            name='Recreation Sites (Points)',
            highlight_function=lambda x: {'fillOpacity': 0.8},
            popup=rec_pop_point,
            zoom_on_click=True
).add_to(rec_marker_cluster)

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
            show=False 
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
            popup=cw_pop,
            show=False    
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
            
            popup=nass_wla_pop,
).add_to(m)

gc.collect()

uwr_pop_goat = folium.GeoJsonPopup(fields=uwr_mountain_goat[['SPECIES_1', 'SPECIES_2']].columns.tolist(),
                            aliases=['Species 1', 'Species 2'])

folium.GeoJson(uwr_mountain_goat, 
                name='Ungulate Winter Range- Mountain Goat (M-ORAM)',
                style_function=lambda feature:{
                    "fillColor": "#715B2E",
                    "color": "#715B2E",
                    "weight": 2,
                    'fillOpacity': 0.7,                        
                },
                
                popup=uwr_pop_goat,
                show=False
).add_to(m)

ogma_pop = folium.GeoJsonPopup(fields=legal_ogmas[['LEGAL_OGMA_PROVID', 'OGMA_TYPE', 'OGMA_PRIMARY_REASON', 'LEGALIZATION_FRPA_DATE', 'LEGALIZATION_OGAA_DATE', 'ASSOCIATED_ACT_NAME']].columns.tolist(),
                                aliases=['OGMA ID', 'OGMA Type', 'OGMA Primary Reason', 'Date OGMA FRPA Order Approved', 'Date OGAA Order Approved', 'Associated Act Name'])

folium.GeoJson(legal_ogmas,
                name='Legal Old Growth Managment Areas',
                style_function=lambda feature:{
                    "fillColor": "#0F4721",
                    "color": "#0F4721",
                    "weight": 1.5,
                    'fillOpacity': 0.7,                         
                },
                
                popup=ogma_pop,
                show=False
).add_to(m)


spec_hab_pop = folium.GeoJsonPopup(fields=spec_hab[['STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])

folium.GeoJson(spec_hab,
                name='Legal Planning Objectives - Special Habitats for General Wildlife',
                style_function=lambda feature:{
                    "fillColor": "#7221A6",
                    "color": "#7221A6",
                    "weight": 2,
                    'fillOpacity': 0.7,                       
                },
                
                popup=spec_hab_pop,
                show=False    
).add_to(m)


vli_pop = folium.GeoJsonPopup(fields=visual_landscape_inventory[['PROJECT_NAME','REC_EVC_FINAL_VALUE_CODE', 'REC_EVQO_CODE', 'RATIONALE']].columns.tolist(),
                                aliases=['Project Name','Existing visual condition (EVC) final value', 'Visual Quality Objective Code', 'Rationale'])

folium.GeoJson(visual_landscape_inventory,
                name='Visual Landscape Inventory',
                style_function=lambda feature:{
                    "fillColor": "#4CBB17",
                    "color": "#4CBB17",
                    "weight": 0.7,
                    'fillOpacity': 0.7
                },
                
                popup=vli_pop,
                show=False    
).add_to(m)

parcel_pop = folium.GeoJsonPopup(fields=private_parcels[['PARCEL_NAME', 'OWNER_TYPE']].columns.tolist(),
                                aliases=['Parcel Name', 'Owner Type'])

parcel_layer = folium.GeoJson(private_parcels,
                name="Private Land",
                style_function=lambda feature:{
                        "fillColor": "#FF5214",
                        "color": "#FF5214",
                        "weight": 0.7,
                        'fillOpacity': 0.7    
                },
                
                popup=parcel_pop,
                show=False
).add_to(m)

nass_area_pop=folium.GeoJsonPopup(fields=nass_area[['TREATY_AREA_ID','TREATY','EFFECTIVE_DATE','FIRST_NATION_NAME','AREA_TYPE','CHAPTER_REFERENCE','APPENDIX_REFERENCE']].columns.tolist(),
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
            
            popup=nass_area_pop,  
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
            
            popup=min_pot_pop,
            show=False    
).add_to(m)

k_srmp_pop=folium.GeoJsonPopup(fields=kalum_srmp[['STRGC_LAND_RSRCE_PLAN_ID','STRGC_LAND_RSRCE_PLAN_NAME','PLAN_TYPE','PLAN_STATUS','APPROVAL_DATE','APPROVAL_LAST_AMEND_DATE','LEGALIZATION_DATE','LEGALIZATION_LAST_AMEND_DATE']].columns.tolist(),
                            aliases=['Strgc Land Rsrce Plan Id', 'Strgc Land Rsrce Plan Name', 'Plan Type', 'Plan Status', 'Approval Date', 'Approval Last Amend Date', 'Legalization Date', 'Legalization Last Amend Date'
])
folium.GeoJson(kalum_srmp,
            name= 'Kalum SRMP',
            style_function=lambda feature:{
                'fillColor':'#FFFFFF',
                "fillPattern": stripes_45,
                'color':'#FFFFFF',
                'weight': 2,
                'fillOpacity': 1.0
            },
            
            popup=k_srmp_pop,
            show=True    
).add_to(m)

k_lrmp_pop=folium.GeoJsonPopup(fields=kalum_lrmp[['STRGC_LAND_RSRCE_PLAN_ID','STRGC_LAND_RSRCE_PLAN_NAME','PLAN_TYPE','PLAN_STATUS','APPROVAL_DATE','APPROVAL_LAST_AMEND_DATE','LEGALIZATION_DATE','LEGALIZATION_LAST_AMEND_DATE']].columns.tolist(),
                            aliases=['Strgc Land Rsrce Plan Id', 'Strgc Land Rsrce Plan Name', 'Plan Type', 'Plan Status', 'Approval Date', 'Approval Last Amend Date', 'Legalization Date', 'Legalization Last Amend Date'
])
folium.GeoJson(kalum_lrmp,
            name= 'Kalum LRMP',
            style_function=lambda feature:{
                'fillColor':'#7B80CE',
                "fillPattern": stripes_45,
                'color':'#7B80CE',
                'weight': 2,
                'fillOpacity': 1.0
            },
            
            popup=k_lrmp_pop,
            show=True    
).add_to(m)

c_lrmp_pop=folium.GeoJsonPopup(fields=cranberry_srmp[['STRGC_LAND_RSRCE_PLAN_ID','STRGC_LAND_RSRCE_PLAN_NAME','PLAN_TYPE','PLAN_STATUS','APPROVAL_DATE','APPROVAL_LAST_AMEND_DATE','LEGALIZATION_DATE','LEGALIZATION_LAST_AMEND_DATE']].columns.tolist(),
                            aliases=['Strgc Land Rsrce Plan Id', 'Strgc Land Rsrce Plan Name', 'Plan Type', 'Plan Status', 'Approval Date', 'Approval Last Amend Date', 'Legalization Date', 'Legalization Last Amend Date'
])
folium.GeoJson(cranberry_srmp,
            name= 'Cranberry SRMP',
            style_function=lambda feature:{
                'fillColor':'#458C78',
                "fillPattern": stripes_45,
                'color':'#458C78',
                'weight': 2,
                'fillOpacity': 1.0
            },
            
            popup=c_lrmp_pop,
            show=True    
).add_to(m)

ht_popup=folium.GeoJsonPopup(fields=hanna_tintina[['ADMIN_AREA_SID','CONSERVANCY_AREA_NAME','ORCS_PRIMARY','ORCS_SECONDARY','ESTABLISHMENT_DATE','OFFICIAL_AREA_HA','PARK_MANAGEMENT_PLAN_URL']].columns.tolist(),
                            aliases=['Admin Area Sid', 'Conservancy Area Name', 'Orcs Primary', 'Orcs Secondary', 'Establishment Date', 'Official Area Ha', 'Park Management Plan Url'])
folium.GeoJson(hanna_tintina,
            name= 'Hanna-Tintina Conservancy',
            style_function=lambda feature:{
                'fillColor':'#104308',
                'color':'#FFFFFF',
                'weight': 2,
                'fillOpacity': 0.7
            },
            
            popup=ht_popup,
            show=False    
).add_to(m) 

water_mgmt_popup=folium.GeoJsonPopup(fields=water_mgmt[['STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])

folium.GeoJson(water_mgmt,
                name='Water Management Units', 
                style_function=lambda feature:{
                'fillColor':'#7AA7F4',
                "fillPattern": stripes_135,
                'color':'#7AA7F4',
                'weight': 2,
                'fillOpacity': 1.0
            },
            
            popup=water_mgmt_popup,
            show=False    
).add_to(m)

uwr_pop_moose = folium.GeoJsonPopup(fields=uwr_moose[['SPECIES_1', 'SPECIES_2']].columns.tolist(),
                            aliases=['Species 1', 'Species 2'])

folium.GeoJson(uwr_moose, 
                name='Ungulate Winter Range- Moose (M-ALAL)',
                style_function=lambda feature:{
                    "fillColor": "#8C0773",
                    "color": "#8C0773",
                    "weight": 2,
                    'fillOpacity': 1.0                       
                },
                
                popup=uwr_pop_moose,
                show=False    
).add_to(m)

rmp_non_legal_moose_pop=folium.GeoJsonPopup(fields=rmp_nonlegal_moose[['NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME','NON_LEGAL_FEAT_OBJECTIVE','ORIGINAL_DECISION_DATE']].columns.tolist(),
                            aliases=['Non Legal Feature ID', 'Strategic Land Resource Plan Name','Non Legal Feature Objective','Original Decision Date'])
folium.GeoJson(rmp_nonlegal_moose, 
                name='Non Legal Planning Features - Current - Polygon: Moose Winter Range',
                style_function=lambda feature:{
                    "fillColor": "#9ceed7",
                    "color": "#9ceed7",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=rmp_non_legal_moose_pop,
                show=False
).add_to(m)


rmp_legal_moose_pop=folium.GeoJsonPopup(fields=rmp_legal_moose[['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.tolist(),
                                                        aliases=['Legal Feature ID','Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])
folium.GeoJson(rmp_legal_moose, 
                name='Legal Planning Features - Current - Polygon: Moose Winter Range',
                style_function=lambda feature:{
                    "fillColor": "#829438",
                    "color": "#829438",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=rmp_legal_moose_pop,
                show=False
).add_to(m)


mta_hist_ten_pop=folium.GeoJsonPopup(fields=aquired_tenures_hist[['TENURE_HISTORY_ID', 'TENURE_NUMBER_ID','TENURE_TYPE_DESCRIPTION','REVISION_NUMBER']].columns.tolist(),
                            aliases=['Tenure History ID', 'Tenure Number ID','Tenure Type','Revision Number'])
folium.GeoJson(aquired_tenures_hist, 
                name='MTA - Mineral, Placer and Coal Tenure History',
                style_function=lambda feature:{
                    "fillColor": "transparent",
                    "color": "#ed7e49",
                    "weight": 2                       
                },
                popup=mta_hist_ten_pop,
                show=False
                ).add_to(m)

def tenure_style_function(feature):
    tenure_type = feature['properties']['TENURE_TYPE_CODE']
    
    # Define colors for each tenure type
    colors = {
        'M':'#24d564', 
        'P':'#f1cb47', 
        'C':'#626b65'     
    }
    
    # Return the style with color based on tenure_type
    return {
        'fillColor': colors.get(tenure_type, 'gray'),  # Default to gray if tenure_type is not found
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.6
    }

mta_ten_pop=folium.GeoJsonPopup(fields=aquired_tenures_curr[['TENURE_NUMBER_ID', 'CLAIM_NAME','TENURE_TYPE_DESCRIPTION','TENURE_SUB_TYPE_DESCRIPTION','TITLE_TYPE_DESCRIPTION','ISSUE_DATE','GOOD_TO_DATE','AREA_IN_HECTARES','REVISION_NUMBER']].columns.tolist(),
                            aliases=['Tenure Number ID', 'Claim Name','Tenure Type Description','Tenure Sub Type Description','Title Type Description', 'Issue Date','Good To Date','Area (ha)',' Revision Number'])
folium.GeoJson(aquired_tenures_curr, 
                name='MTA - Mineral, Placer and Coal Tenure',
                style_function=tenure_style_function,
                            
                popup=mta_ten_pop,
                show=False
).add_to(m)

wha_grizz_pop=folium.GeoJsonPopup(fields=wha_grizzly[['HABITAT_AREA_ID', 'TAG','APPROVAL_DATE','FEATURE_NOTES','COMMON_SPECIES_NAME','LEGISLATION_ACT_NAME','TIMBER_HARVEST_CODE','HECTARES']].columns.tolist(),
                            aliases=['Habitat Area ID', 'Tag','WHA Approval Date','Feature Notes','Common Species Name','Legislation Act Name','Timber Harvest Code','Area(ha)'])
folium.GeoJson(wha_grizzly, 
                name='Wildlife Habitat Areas - Approved: Grizzly Bear',
                style_function=lambda feature:{
                    "fillColor": "#d099ec",
                    "color": "#d099ec",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=wha_grizz_pop,
                show=False    
).add_to(m)

legal_ghawk_pop=folium.GeoJsonPopup(fields=legal_g_hawk_nesting[['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Legal Feature ID','Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])
folium.GeoJson(legal_g_hawk_nesting, 
                name='Legal Planning Objectives - Current - Polygon: Goshawk Nesting and Fledging Areas',
                style_function=lambda feature:{
                    "fillColor": "#dbec99",
                    "color": "#dbec99",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=legal_ghawk_pop,
                show=False    
).add_to(m)

non_legal_ghawk_pop=folium.GeoJsonPopup(fields=non_legal_g_hawk_nesting[['NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME','NON_LEGAL_FEAT_OBJECTIVE','ORIGINAL_DECISION_DATE']].columns.tolist(),
                            aliases=['Non Legal Feature ID', 'Strategic Land Resource Plan Name','Non Legal Feature Objective','Original Decision Date'])
folium.GeoJson(non_legal_g_hawk_nesting, 
                name='Non Legal Planning Objectives - Current - Polygon: Goshawk Nesting and Fledging Areas',
                style_function=lambda feature:{
                    "fillColor": "#dbec99",
                    "color": "#dbec99",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=non_legal_ghawk_pop,
            show=False    
).add_to(m)

gc.collect()


eca_pop=folium.GeoJsonPopup(fields=eca_threshold[['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Legal Feature ID','Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])
folium.GeoJson(eca_threshold, 
                name='Legal Planning Objectives - Current - Polygon: Equivalent Clearcut Area Threshold Watersheds',
                style_function=lambda feature:{
                    "fillColor": "#99b1ec",
                    "color": "#99b1ec",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=eca_pop,
                show=False    
).add_to(m)

eco_net_pop=folium.GeoJsonPopup(fields=ecosystem_net[['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Legal Feature ID','Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])
folium.GeoJson(ecosystem_net, 
                name='Legal Planning Objectives - Current - Polygon: Ecosystem Network',
                style_function=lambda feature:{
                    "fillColor": "#f1906d",
                    "color": "#f1906d",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=eco_net_pop,
                show=False    
).add_to(m)


ecosystem_buf_pop=folium.GeoJsonPopup(fields=ecosystem_buf[['NON_LEGAL_FEAT_ID', 'STRGC_LAND_RSRCE_PLAN_NAME','NON_LEGAL_FEAT_OBJECTIVE','ORIGINAL_DECISION_DATE']].columns.tolist(),
                            aliases=['Non Legal Feature ID', 'Strategic Land Resource Plan Name','Non Legal Feature Objective','Original Decision Date'])
folium.GeoJson(ecosystem_buf, 
                name='Non Legal Planning Objectives - Current - Polygon: Ecosystem Network Buffer',
                style_function=lambda feature:{
                    "fillColor": "#f1906d",
                    "color": "#f1906d",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=ecosystem_buf_pop,
                show=False    
).add_to(m)
cedar_pop=folium.GeoJsonPopup(fields=cedar_reserves[['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Legal Feature ID','Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])
folium.GeoJson(cedar_reserves, 
                name='Legal Planning Objectives - Current - Polygon: Cedar Stand Reserves',
                style_function=lambda feature:{
                    "fillColor": "#8cf16d",
                    "color": "#8cf16d",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=cedar_pop,
                show=False    
).add_to(m)


griz_wtrshd_pop=folium.GeoJsonPopup(fields=griz_wtrshd[['LEGAL_FEAT_ID','STRGC_LAND_RSRCE_PLAN_NAME', 'LEGAL_FEAT_OBJECTIVE', 'LEGALIZATION_DATE', 'ENABLING_DOCUMENT_TITLE', 'ENABLING_DOCUMENT_URL', 'RSRCE_PLAN_METADATA_LINK']].columns.to_list(),
                                    aliases=['Legal Feature ID','Strategic Land Resource Plan Name', 'Legal Objective Type', 'Legalization Date', 'Legal Order Title', 'Enabling Document URL', 'Resource Plan Metadata Link'])
folium.GeoJson(griz_wtrshd, 
                name='Legal Planning Objectives - Current - Polygon: Grizzly Bear Identified Watersheds',
                style_function=lambda feature:{
                    'fillColor':'#E65C0F',
                    "fillPattern": stripes_135,
                    'color':'#E65C0F',
                    'weight': 2,
                    'fillOpacity': 1.0
                },
                
                popup=griz_wtrshd_pop,
                show=False    
).add_to(m)


parks_pop=folium.GeoJsonPopup(fields=parks_reserves_protected_areas[['ADMIN_AREA_SID','PROTECTED_LANDS_NAME','PROTECTED_LANDS_DESIGNATION','PARK_CLASS','OFFICIAL_AREA_HA','PARK_MANAGEMENT_PLAN_URL']].columns.to_list(),
                                    aliases=['Admin Area ID', 'Protected Lands Name','Protected Lands Designation','Parks Class','Official Area(ha)','Park Management Plan URL'])
folium.GeoJson(parks_reserves_protected_areas, 
                name='BC Parks, Ecological Reserves, and Protected Areas',
                style_function=lambda feature:{
                    "fillColor": "#558131",
                    "color": "#558131",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=parks_pop,
                show=False    
).add_to(m)

# could make all bec zones diff color?
bec_pop=folium.GeoJsonPopup(fields=bec[['MAP_LABEL','ZONE','SUBZONE','VARIANT','PHASE','NATURAL_DISTURBANCE']].columns.to_list(),
                                    aliases=['BEC Label','Zone','Subzone','Variant','Phase','Natural Distrurbance'])
folium.GeoJson(bec, 
                name='Biogeoclimatic Ecosystem Classification (BEC)',
                style_function=lambda feature:{
                    "fillColor": "#B3536A",
                    "color": "#B3536A",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=bec_pop,
                show=False
).add_to(m)

ecosect_pop=folium.GeoJsonPopup(fields=ecosections[['ECOSECTION_CODE','ECOSECTION_NAME','EFFECTIVE_DATE','EXPIRY_DATE']].columns.to_list(),
                                    aliases=['Ecosection Code','Ecosection Name','Effective Date','Expiry Date'])
folium.GeoJson(ecosections, 
                name='Ecosections - Ecoregion Ecosystem Classification',
                style_function=lambda feature:{
                    "fillColor": "#817331",
                    "color": "#817331",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=ecosect_pop,
                show=False
).add_to(m)

fn_ct_pop=folium.GeoJsonPopup(fields=fn_reserves_crown_ten[['INTRID_SID','TENURE_STAGE','TENURE_STATUS','TENURE_TYPE','TENURE_SUBTYPE','TENURE_PURPOSE','CROWN_LANDS_FILE','TENURE_EXPIRY','TENURE_LEGAL_DESCRIPTION','TENURE_AREA_IN_HECTARES']].columns.to_list(),
                                    aliases=['ID','Tenure Stage','Tenure Status','Tenure Type','Tenure Sub-Type','Tenure Purpose','Crown Lands Fire', 'Tenure Expiry','Tenure Legal Description','Area(ha)'])
folium.GeoJson(fn_reserves_crown_ten, 
                name='Treaty Settlemet Lands',
                style_function=lambda feature:{
                    "fillColor": "#C1EA70",
                    "color": "#C1EA70",
                    "weight": 2,
                    'fillOpacity': 0.6                       
                },
                
                popup=fn_ct_pop,
                show=False
).add_to(m)

gc.collect()

#Manage tile layers
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('cartodb positron').add_to(m)
folium.TileLayer('Esri WorldImagery').add_to(m)
folium.TileLayer(show=True).add_to(m)
# add layer control 
folium.LayerControl().add_to(m)

# #group layers
# #lists for grouping dict
# current_non_legal=[]
# current_legal=[water_mgmt_lyr,spec_hab_lyr]
# slrmp=[]
# lrmp=[]
# #grouping dict
# group_dict={'Legal Planning Objectives - Current':current_legal} #, 'Non Legal Planning Objectives - Current':current_non_legal
# #grouped layer call
# GroupedLayerControl(
#     groups=group_dict,
#     collapsed=True,
# ).add_to(m)


#clean up the UUID’s and extra whitespace
html = m.get_root()
res = html.script.get_root().render()
# replace UUID with first 8
ru = r'([0-9a-f]{8})[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12}'
res = re.sub(ru,r'\1',res)
# clean up whitespace
rl = []
for s in res.split('\n'):
    ss = s.strip()
    if len(ss) > 0:
        rl.append(ss)
rlc = '\n'.join(rl)

gc.collect()

#save html map
# print(BASE_DIR)
m.save(os.path.join('LUP_Overview.html')) 


#zip html file 
# # Save as gzipped HTML
# with gzip.open('LUP_Overview.html.gz', 'wb') as f:
#     f.write(rlc.encode('utf-8'))