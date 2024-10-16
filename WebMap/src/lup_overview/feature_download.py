import os
import json
import tempfile
import logging
import requests
import geojson
import geopandas
import pandas
import duckdb
import psutil

logging.basicConfig(level=logging.INFO)
 
class WFS_downloader:
    ''' Downloads data from WFS
    '''
    SERVICE_URL = "https://openmaps.gov.bc.ca/geo/pub/ows?"
    PAGESIZE = 10000
    # http://openmaps.gov.bc.ca/geo/pub/wfs?request=GetCapabilities
    # https://openmaps.gov.bc.ca/geo/pub/WHSE_FOREST_VEGETATION.VEG_COMP_LYR_R1_POLY/wfs?request=GetCapabilities


    def __init__(self) -> None:
        self.memory_threshold =600000000    #memory threshold in bytes
        self.MEMORY_RATE = 0
        self.CACHE_FILES = []
        self.CACHE_DIR = tempfile.gettempdir()
        self.offset=0
        self.con = duckdb.connect(database=':memory:')
        self.con.install_extension("httpfs")
        self.con.load_extension("httpfs")
        self.con.execute("INSTALL spatial;")
        self.con.execute("LOAD spatial;")
        self.data_geom_column = None
        self.data_crs = None
        self.max_retries = 5


    def create_bbox(self, aoi):
        ''' Create bounding box coordinate tuple'''
        
        if not isinstance(aoi, geopandas.GeoDataFrame):
            df=geopandas.read_file(aoi)
        else:
            df=aoi
        df=df.dissolve()
        aoi_bounds= df.total_bounds.tolist()
        bbox=['%.0f' % elem for elem in aoi_bounds]
        bbox=[int(x) for x in bbox]
        bbox.append("urn:ogc:def:crs:EPSG:3005")
        bbox=tuple(bbox)
        logging.info(f"Bounding box coords: {bbox}")
        return bbox
    
    
    def adjust_pagesize_by_memory(self, current_pagesize, available_memory):
        '''Funtion to adjust page size by available memory at time function is called'''
        
        #in bytes
        if available_memory < self.memory_threshold:
            adjusted_pagesize=max(current_pagesize // 2, 1)
            logging.info(f"Adjusting pagesize to {adjusted_pagesize} due to low memory.")
            return adjusted_pagesize
        else:
            return 10000
    
    
    def __data_cache__(self,features):
        ''' Cache data for large downloads'''
        
        if len(features) >0:
            dump_count = len(self.CACHE_FILES)
            cache_file = os.path.join(self.CACHE_DIR,f'cache_{str(dump_count)}.parquet')
            fc = geojson.FeatureCollection(features=features)
            df = geopandas.GeoDataFrame.from_features(fc['features'])
            df.to_parquet(cache_file)
            self.CACHE_FILES.append(cache_file)
            logging.debug(f"chache file list {self.CACHE_FILES}")
            logging.debug(f'Cached features: {cache_file}')
            self.offset = dump_count
            all_features=[]
            return True
    
    
    def __load_cache_to_dataframe__(self) -> geopandas.GeoDataFrame:
        '''Load all cache data and merge into one GeoParquet'''
     
        logging.info('Loading cache to GeoDataFrame')
        parquet_files = [file for file in os.listdir(self.CACHE_DIR) if file.endswith('.parquet')]
        if not parquet_files:
            logging.warning('No Parquet files found in the cache directory.')
            return geopandas.GeoDataFrame()

        geo_dfs = []
        for parquet_file in parquet_files:
            file_path = os.path.join(self.CACHE_DIR, parquet_file)
            geo_df = geopandas.read_parquet(file_path)
            geo_dfs.append(geo_df)

        concatenated_gdf = geopandas.GeoDataFrame(pandas.concat(geo_dfs, ignore_index=True))

        if self.data_crs is not None:
            concatenated_gdf.crs = self.data_crs

        return concatenated_gdf
    
    
    def get_data(self, dataset, query=None, fields=None, bbox=None):
        '''Returns dataset in json format
        params:
            query: CQL formated query
            fields: comma deliminated str
            bbox: comma delimited float values in EPSG:3005 metres
        
        example usage:
        wfs = WFS_downloader
        r = wfs.get_data('WHSE_IMAGERY_AND_BASE_MAPS.GSR_AIRPORTS_SVW')
        TODO: discover OBJECTID , discover GEOMETRY Column name (SHAPE,GEOMETRY,geom,the_geom)
        '''
        
        pagesize = self.PAGESIZE
        availiable_memory = psutil.virtual_memory().available
        logging.info(f"Memory available: {availiable_memory}")

        r = self.wfs_query(dataset=dataset, query=query, fields=fields, bbox=bbox)
        matched = int(r.get('numberMatched'))
        returned = int(r.get('numberReturned'))
        logging.debug(f"matched features {matched}")
        logging.info(f"returned features {returned}")
        if self.data_crs is None:
            self.data_crs = r['crs']['properties']['name'].split('crs:')[1].replace('::', ':')
        features = r.get('features')
        if self.data_geom_column is None:
            self.data_geom_column = features[0]['geometry_name'].lower()

        while returned < matched:
            
            pagesize=self.adjust_pagesize_by_memory(self.PAGESIZE, psutil.virtual_memory().available)
            logging.debug(f'page is {pagesize}')
            
            logging.debug("")
            start_index = returned
            current_features = self.wfs_query(dataset=dataset, query=query, fields=fields, bbox=bbox,
                                              start_index=start_index, count=pagesize)
            returned += int(current_features.get('numberReturned'))
            logging.info(f"total returned features {returned}")
            features += current_features.get('features')
            logging.debug(f"features on deck {len(features)}")
            self.MEMORY_RATE = availiable_memory - psutil.virtual_memory().available
            logging.debug(f"memory rate {self.MEMORY_RATE}")
            if not current_features:
                break

            if len(features) >= pagesize:
                logging.debug(f"# of features {len(features)}")
                self.__data_cache__(features=features)
                
            features = []
                
        if len(self.CACHE_FILES) > 0:
            # handle cached features
            if len(features) > 0:
                self.__data_cache__(features=features)
                features = []
            df = self.__load_cache_to_dataframe__()
        else:
            df = self.features_to_df(features=features)

        return df


    def wfs_query(self,dataset, query=None, fields=None,bbox=None,start_index = None, count=None): 
        '''Returns dataset in json format'''
        
        if fields is None:
            fields = []
        url = self.SERVICE_URL
        params = {'service':'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': f'pub:{dataset}',
            'outputFormat':'json',
            "srsName": "EPSG:3005",
            'sortBy':'OBJECTID',
            'limit' : 10000,
            'offset': self.offset
            }
        # build optional params
    # build optional params
        if bbox is not None and query is not None:
            # append bbox to cql
            bbox = [str(b) for b in bbox]
            bbox_str = f'BBOX(GEOMETRY,{",".join(bbox)})'
            bbox = [str(b) for b in bbox if b != "urn:ogc:def:crs:EPSG:3005"]
            bbox_str = f'BBOX(GEOMETRY,{",".join(bbox)}, \'urn:ogc:def:crs:EPSG:3005\')'
            query = f'{bbox_str} AND {query}'
        elif bbox is not None:
            bbox = [str(b) for b in bbox]
            params['bbox'] = ",".join(bbox)
        elif query is not None:
            params['CQL_FILTER']=query
                    
        if query:
            params['CQL_FILTER']=query
        if len(fields)>0:
            params['propertyName']=','.join(fields).upper()
        
        # pagenation
        if start_index:
            params['startIndex'] = start_index
        if count:
            params['count'] = count
            
        for attempt in range (self.max_retries):
            r = requests.get(url, params)
            logging.debug(f"WFS URL request: {r.url}")
            if r.status_code == 502:
                logging.warning(f"502 Bad Gateway. Retrying ({attempt + 1}/{self.max_retries})...")
            else:
                break

        if r.status_code != 200:
            logging.error(f"Error from WFS service. Status code: {r.status_code}")
            return {}
        
        if not r.text:
            logging.warning("Empty response received from WFS service.")
            return {}
        
        return r.json()
       
       
    def features_to_df(self,features) -> geopandas.GeoDataFrame:
        ''' Creates Geopandas GeoDataFrame from 
            list of geojson features result
        params:
            features: list of GeoJson Features
        usage:
            wfs.to_df(features)
        '''
        logging.debug(f'Loading {len(features)} features to GeoDataFrame')
        fc = geojson.FeatureCollection(features=features)
        df = geopandas.GeoDataFrame.from_features(fc['features'])
        logging.debug(f'Loading Complete')
        return df
    
    
    def features_to_geojson(self,features,output) ->str:
        ''' Writes WFS result to geojson file
        params:
            wfs_result: json wfs response from get_data
            output: output file path (str)
        usage:
            wfs.to_geojson(r,'T:/data/airports.geojson)
        '''
        collection = geojson.FeatureCollection(features=features)
        with open(output,'w') as f:
            geojson.dump(collection,f)
            
            
    def geojson_from_file(self,geojson_file):
        ''' Reads GeoJson file to list of features (GeoJSON)
        params:
            geojson_file: geojson file
        returns: list of geojson features
        usage:
            wfs.features_from_geojson('T:/data/airports.geojson)
        '''
        with open(geojson_file,'r') as f:
            obj = geojson.load(f)
        return obj
