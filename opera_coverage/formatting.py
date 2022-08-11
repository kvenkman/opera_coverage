from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from rasterio.crs import CRS
from warnings import warn
from copy import deepcopy as dc

# for formatting the datetime object to asfsearch syntax
def datetime2asfsearch(entered_date: datetime) -> str:
    return datetime.strftime(entered_date,'%Y') + '-' + datetime.strftime(entered_date,'%m') + '-' + datetime.strftime(entered_date,'%d') + 'T' + datetime.strftime(entered_date,'%H') + ':' + datetime.strftime(entered_date,'%M') + ':' + datetime.strftime(entered_date,'%S') + 'Z'

# for formatting the asfsearch syntax to datetime object
def asfsearch2datetime(entered_date: str) -> datetime:
    if '+00:00' in entered_date:
        entered_date = entered_date.replace('+00:00','')
    try:
        dtime = datetime.strptime(entered_date, '%Y-%m-%d %H:%M:%S.%f')
    except:
        dtime = datetime.strptime(entered_date, '%Y-%m-%d %H:%M:%S')
    return dtime

# reformat results from asf_search list to geodataframe
def format_results_for_sent1(results: list) -> gpd.GeoDataFrame:
    geometry = [shape(r.geojson()['geometry']) for r in results]
    data = [r.properties for r in results]

    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS.from_epsg(4326))

    if df.empty:
        warn('Sentinel-1 dataframe is empty! Check inputs.')
        return df

    df['sensor'] = ['sentinel1' for i in range(len(df))]
    df['startTime'] = pd.to_datetime(df.startTime).dt.tz_convert('UTC')
    df['stopTime'] = pd.to_datetime(df.stopTime).dt.tz_convert('UTC')
    # df['start_date'] = pd.to_datetime(df.startTime.dt.date)
    # df['start_date_str'] = df.start_date.dt.date.map(str)
    # df['pathNumber'] = df['pathNumber'].astype(int)
    # df = df.sort_values(by=['startTime', 'pathNumber']).reset_index(drop=True)
    # df.drop(columns=['browse','beamModeType','bytes','centerLat','centerLon','faradayRotation','flightDirection','groupID','granuleType','insarStackId','md5sum','offNadirAngle','orbit','pathNumber','platform','pointingAngle','polarization','processingDate','processingLevel','sceneName','url','fileName','frameNumber','stopTime'], inplace=True)
    df = df.sort_values(by=['startTime']).reset_index(drop=True)
    df = df.reindex(columns=['startTime','geometry','sensor','fileID'])

    return df

# reformat results from hls_search list to geodataframe
def format_results_for_hls(results: list, sensor: str) -> gpd.GeoDataFrame:
    geometry = [shape(results[r].geometry) for r in range(len(results))]
    data = [results[r].properties for r in range(len(results))]
    # print(len(data))

    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS.from_epsg(4326))

    if df.empty:
        if 'sentinel2' in sensor.lower():
            warn('Sentinel-2 dataframe is empty! Check inputs.')
        elif 'landsat8' in sensor.lower():
            warn('Landsat-8 dataframe is empty! Check inputs.')
        return df
    
    df['sensor'] = [sensor for i in range(len(df))]
    df['startTime'] = pd.to_datetime(df.start_datetime.replace('Z',''))
    df['start_date'] = df.startTime.dt.strftime('%Y%m%d%H')
    df['fileID'] = [results[i].id for i in range(len(results))]
    df = df.sort_values(by=['startTime']).reset_index(drop=True)
    df = df.dissolve(by='start_date')
    # df.drop(['datetime','start_datetime','end_datetime'], axis=1, inplace=True)
    df = df.reindex(columns=['startTime','geometry','sensor','fileID'])
    df = df.dissolve(by='startTime').reset_index()

    return df

# convert a shapely object (point or polygon) to geodataframe
def shape2gdf(shape, filename = None, to_file = True) -> gpd.GeoDataFrame:
    data = {}
    data['coordinates'] = [shape.wkt]
    data['coordinates'] = gpd.GeoSeries.from_wkt(data['coordinates'])
    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry = 'coordinates', crs=CRS.from_epsg(4326))
    if to_file:
        df.to_file(filename + '.geojson',driver='GeoJSON')
    
    return df

# for sensors that have acquisitions less than 5 seconds apart, merge the geometries and regard as one acquisition
def drop(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    dfc = dc(df)
    for i in range(len(df) - 1):
        if (df.startTime[i + 1] - df.startTime[i]).seconds < 5:
            dfc.geometry[i] = dfc.geometry[i].union(dfc.geometry[i + 1])
            dfc = dfc.drop([i + 1])
    dfc = dfc.reset_index(drop=True)
    return dfc