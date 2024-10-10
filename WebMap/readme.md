#   Land Use Plan Open Source Web Application

The Land Use Plan (LUP) is an amalgamation of existing land use plans that overlap with the AOI. This project aims to provide an efficient way to spatially identify relevant non-legal and legal objectives. Additionally, the data needs to be compared against what is publicly accessible through the LUP website to ensure alignment.

To download the Land Use Plan shapefiles as a zip folder, contact Cole

## Deliverables

- An internal web application that consolidates all relevant data from British Columbia to compare against the public data (see the `data_source.xlsx` for details on layers).
- Display and query the SRMP/LRMP layers clipped to the LUP boundary.
- Ability to add a KML, geomark, shapefile, or Area of Interest (AOI) as a temporary layer to the web map.
- Identify overlaps in the SRMP/LRMP data and potentially export the tabular data, similar to a mini status report.
- If possible, add links on the Skeena Data Hub to centralize all information in one location.


# Create Conda Environment and Upgrade Folium, GeoPandas, and Flask
## Be patient; the geospatial package takes a while.
```bash
conda create -n open_geo -c conda-forge python>=3.11 geospatial folium geopandas flask
```
 
# Activate the Environment
```bash
conda activate open_geo
```

# In VS Code
1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS).
2. Search for **Python: Select Interpreter**.
3. Choose the `open_geo` environment from the list.

# For help with conda, see the link below: 
[getting started](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html)

