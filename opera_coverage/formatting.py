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

    df['startTime'] = pd.to_datetime(df.startTime).dt.tz_convert('UTC')
    df['stopTime'] = pd.to_datetime(df.stopTime).dt.tz_convert('UTC')
    df = df.sort_values(by=['startTime']).reset_index(drop=True)
    df['new_start_date'] = df.startTime.dt.strftime('%Y%m%d%H')
    df['new_start_date'] = df.apply(lambda row: row['new_start_date'] + '_' + str(row['pathNumber']), axis=1)

    new_start_time = [sorted(df[df.new_start_date == i].startTime)[0] for i in df.new_start_date.unique()]
    new_geometry = [df[df.new_start_date==i].geometry.unary_union for i in df.new_start_date.unique()]
    new_fileids = [','.join(df[df.new_start_date==i].fileID) for i in df.new_start_date.unique()]
    df = {'startTime':new_start_time, 'fileID':new_fileids}
    df['sensor'] = 'sentinel1'
    df = pd.DataFrame(data = df)
    df = gpd.GeoDataFrame(df, geometry=new_geometry, crs=CRS.from_epsg(4326))
    df = df.reindex(columns=['startTime','geometry','sensor','fileID'])

    return df

# reformat results from hls_search list to geodataframe
def format_results_for_hls(results: list, sensor: str) -> gpd.GeoDataFrame:
    geometry = [shape(results[r].geometry) for r in range(len(results))]
    data = [results[r].properties for r in range(len(results))]

    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS.from_epsg(4326))

    if df.empty:
        if 'sentinel2' in sensor.lower():
            warn('Sentinel-2 dataframe is empty! Check inputs.')
        elif 'landsat8' in sensor.lower():
            warn('Landsat-8 dataframe is empty! Check inputs.')
        return df
    
    df['startTime'] = pd.to_datetime(df.start_datetime.replace('Z',''))
    df['fileID'] = [results[i].id for i in range(len(results))]
    df = df.sort_values(by=['startTime']).reset_index(drop=True)
    df['new_start_date'] = df.startTime.dt.strftime('%Y%m%d%H')

    new_start_time = [sorted(df[df.new_start_date == i].startTime)[0] for i in df.new_start_date.unique()]
    new_geometry = [df[df.new_start_date==i].geometry.unary_union for i in df.new_start_date.unique()]
    new_fileids = [','.join(df[df.new_start_date==i].fileID) for i in df.new_start_date.unique()]
    df = {'startTime':new_start_time, 'fileID':new_fileids}
    df['sensor'] = sensor
    df = pd.DataFrame(data = df)
    df = gpd.GeoDataFrame(df, geometry=new_geometry, crs=CRS.from_epsg(4326))
    df = df.reindex(columns=['startTime','geometry','sensor','fileID'])

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