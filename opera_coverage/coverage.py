from typing import List
from shapely.geometry import Polygon
from datetime import datetime
import numpy as np
from . import formatting as f
from . import search as s
# from . import plotting as p

def get_coverage(sensor: List[str], aoi: Polygon, date: List[datetime] = None) -> List[dict]:
    """
    Sensor: choose sentinel1, sentinel2, landsat8
    AOI: enter coordinates as Polygon object
    date: leave as none if searching today, else enter time range as datetime tuple: datetime(YYYY,MM,DD)
    """
    # freq = {}
    # next_acq = {}
    # area = {}
    dataframes = []
    
    for sensor_name in sensor:
        # freq[sensor_name] = ''
        # next_acq[sensor_name] = ''
        # area[sensor_name] = ''
        
        if 'landsat8' in sensor_name.lower():
            results = s.hls_search('landsat8', aoi, date)
            df = f.format_results_for_hls(results,'landsat8')
        elif 'sentinel1' in sensor_name.lower():
            results = s.asf_search(aoi, date)
            df = f.format_results_for_sent1(results)
        elif 'sentinel2' in sensor_name.lower():
            results = s.hls_search('sentinel2', aoi, date)
            df = f.format_results_for_hls(results,'sentinel2')
        
        dataframes.append(df)

        # # return cadence as string or list using get_cadence
        # freq[sensor_name] = s.get_cadence(df)
        
        # # find next acquisition time, if search time is today then returns 'N/A'
        # if date == None:
        #     next_acq[sensor_name] = 'N/A'
            
        # else:
        #     next_acq[sensor_name] = 'Time of next acquisition after ' + str(date[1]) + ' is ' + str(s.acq_search(sensor_name.lower(), aoi, date[1]))
        
        # # find intersection of acquisitions from each sensor separately
        # if len(results) == 0:
        #     area[sensor_name] = 0
        # else:
        #     area[sensor_name] = df.geometry[0]
            
        #     if len(results) > 1:
                
        #         for i in range(len(df) - 1):
        #             area[sensor_name] = area[sensor_name].intersection(df.geometry[i + 1])

    coverage_df = s.get_sensor_cadence(dataframes)
    return coverage_df
    # return freq, next_acq, area, master

def get_global_coverage(sensor: List[str], gridsize, date: List[datetime]) -> np.array:
    long_block = np.linspace(-180, 180, gridsize[0] + 1)
    lat_block = np.linspace(90, -90, gridsize[1] + 1)

    value = np.zeros([(len(lat_block) - 1),(len(long_block) - 1)])
    for i in range(len(long_block) - 1):
        for j in range(len(lat_block) - 1):
            aoi = Polygon([[long_block[i], lat_block[j]],[long_block[i + 1], lat_block[j]],[long_block[i + 1], lat_block[j + 1]],[long_block[i], lat_block[j + 1]]])

            for sensor_name in sensor:    
                if 'landsat8' in sensor_name.lower():
                    results = s.hls_search('landsat8', aoi, date)
                elif 'sentinel1' in sensor_name.lower():
                    results = s.asf_search(aoi, date)
                elif 'sentinel2' in sensor_name.lower():
                    results = s.hls_search('sentinel2', aoi, date)

                value[j][i] += len(results)

    # p.heatmap(value, long_block, lat_block)

    return value