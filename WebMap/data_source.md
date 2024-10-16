# Overvew Map
- Def Query may give you exact results where bbox may be more appropriate (1112127, 743161, 1291755, 898012, "urn:ogc:def:crs:EPSG:3005")
- map may need feature to upload user input layer
- map may need grouping plugins

| Assigned to | BCGW Layer                                               | Def Query                                                        |
|-------------|-----------------------------------------------------------|------------------------------------------------------------------|
| Cole        | WHSE_FOREST_TENURE.FTEN_REC_SITE_POINTS_SVW               | Apply bounding box                                               |
| Cole        | WHSE_FOREST_TENURE.FTEN_RECREATION_POLY_SVW               | Apply bounding box                                               |
| Cole        | WHSE_WATER_MANAGEMENT.WLS_COMMUNITY_WS_PUB_SVW            | WLS_CW_SYSID = 33                                                |
| Cole        | WHSE_LEGAL_ADMIN_BOUNDARIES.FNT_TREATY_AREA_SP            | TREATY = 'Nisga''a'                                              |
| Cole        | WHSE_LEGAL_ADMIN_BOUNDARIES.FNT_TREATY_AREA_SP            | TREATY = 'Nisga''a'                                              |
| Cole        | WHSE_MINERAL_TENURE.MINPOT_MINERAL_POTENTIAL              | Apply bounding box                                               |
| Cole        | WHSE_LAND_USE_PLANNING.RMP_STRGC_LAND_RSRCE_PLAN_SVW      | STRGC_LAND_RSRCE_PLAN_ID = 20                                   |
| Cole        | WHSE_TANTALIS.TA_CONSERVANCY_AREAS_SVW                    | ADMIN_AREA_SID = 5420                                            |
| Cole        | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Water Management Units'               |
| Emma        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Water Management Units'                   |
| Emma        | WHSE_FOREST_VEGETATION.REC_VISUAL_LANDSCAPE_INVENTORY     | Apply bounding box                                               |
| Emma        | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Special Habitats for General Wildlife'|
| Emma        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Special Habitats for General Wildlife'    |
| Emma        | WHSE_FOREST_TENURE.FTEN_RECREATION_POLY_SVW               | Apply bounding box                                               |
| Emma        | WHSE_CADASTRE.PMBC_PARCEL_FABRIC_POLY_FA_SVW              | OWNER_TYPE = 'Private'                                           |
| Emma        | WHSE_LAND_USE_PLANNING.RMP_OGMA_LEGAL_CURRENT_SVW         | Apply bounding box                                               |
| Emma        | WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP     | Apply bounding box and SPECIES_1 = 'M-ORAM' Or (SPECIES_2 = 'M-ORAM')|
| Maddi       | WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP     | SPECIES_1 IN ('M-ALAL', 'M-ALAL;M-CEEL;M-ODHE;M-ODVI') Or SPECIES_2 IN ('M-ALAL', 'M-ODHE; M-ALAL') |
| Maddi       | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Moose Winter Range'                   |
| Maddi       | WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_HISTORY_SP        | Apply bounding box                                               |
| Maddi       | WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW               | Apply bounding box                                               |
| Maddi       | WHSE_WILDLIFE_MANAGEMENT.WCP_WILDLIFE_HABITAT_AREA_POLY   | COMMON_SPECIES_NAME = 'Grizzly Bear'                             |
| Maddi       | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Goshawk Nesting/Post-Fledging Habitat' And STRGC_LAND_RSRCE_PLAN_NAME IN ('Cranberry Sustainable Resource Management Plan', 'Nass South Sustainable Resource Management Plan')|
| Maddi       | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Goshawk Nesting/Post-Fledging Habitat' And STRGC_LAND_RSRCE_PLAN_NAME IN ('Cranberry Sustainable Resource Management Plan', 'Nass South Sustainable Resource Management Plan')|
| Eric        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Special Habitats for General Wildlife'    |
| Eric        | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Special Habitats for General Wildlife'|
| Eric        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Water Management Units'                   |
| Eric        | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Water Management Units'               |
| Eric        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Equivalent Clearcut Area Threshold Watersheds'|
| Eric        | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | LEGAL_FEAT_OBJECTIVE = 'Equivalent Clearcut Area Threshold Watersheds'|
| Tara        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Ecosystem Network'                    |
| Tara        | WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW            | LEGAL_FEAT_OBJECTIVE = 'Cedar Stand Reserves'                      |
| Tara        | WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW        | NON_LEGAL_FEAT_OBJECTIVE = 'Mountain Goat Winter Range' * incorrect           |
| Tara        | WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP     | SPECIES_1 LIKE %'M-ORAM' OR SPECIES_2 LIKE %'M-ORAM'             |
| Tara        | WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW                       | Apply bounding box                                               |
| Tara        | WHSE_FOREST_VEGETATION.BEC_BIOGEOCLIMATIC_POLY            | Apply bounding box                                               |
| Tara        | WHSE_TERRESTRIAL_ECOLOGY.ERC_ECOSECTIONS_SP               | Apply bounding box                                               |
| Tara        | WHSE_TANTALIS.TA_CROWN_TENURES_SVW                        | TENURE_TYPE = 'RESERVE/NOTATION'                                  |
<br>
<br>

# Land Use Planning Features Map
- bbox  (1112127, 743161, 1291755, 898012, "urn:ogc:def:crs:EPSG:3005")
- map will need query/filtering
- 
| Assigned to | BCGW Layer                                               | Def Query                                                        |
|-------------|-----------------------------------------------------------|------------------------------------------------------------------|
|-------------|WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_LINE_SVW|  apply bounding box|
|-------------|WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_LINE_SVW|  apply bounding box|
|-------------|WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POINT_SVW|  apply bounding box|
|-------------|WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POINT_SVW|  apply bounding box|
|-------------|WHSE_LAND_USE_PLANNING.RMP_PLAN_NON_LEGAL_POLY_SVW|  apply bounding box|
|-------------|WHSE_LAND_USE_PLANNING.RMP_PLAN_LEGAL_POLY_SVW|  apply bounding box|
