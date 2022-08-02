from typing import List
from shapely.geometry import Polygon
from datetime import datetime
from . import formatting as f
from . import search as s

def get_coverage(sensor: List[str], aoi: Polygon, date: List[datetime] = None) -> List[dict]:
    """
    Sensor: choose sentinel1, sentinel2, landsat8
    AOI: enter coordinates as Polygon object
    date: leave as none if searching today, else enter time range as datetime tuple: datetime(YYYY,MM,DD)
    """
    freq = {}
    next_acq = {}
    area = {}
    dataframes = []
    
    for sensor_name in sensor:
        freq[sensor_name] = ''
        next_acq[sensor_name] = ''
        area[sensor_name] = ''
        
        if 'landsat8' in sensor_name.lower():
            results = s.hls_search('landsat8', aoi, date)
            df = f.format_results_for_hls(results,'landsat8')
        elif 'sentinel1' in sensor_name.lower():
            results = s.asf_search(aoi, date)
            df = f.format_results_for_sent1(results)
        elif 'sentinel2' in sensor_name.lower():
            results = s.hls_search('sentinel2', aoi, date)
            df = f.format_results_for_hls(results,'sentinel2')
        
        try:
            df = df.dissolve(by='start_date').reset_index()
            df.drop(['start_date'],inplace=True)
        except:
            pass
        
        dataframes.append(df)

        # return cadence as string or list using get_cadence
        freq[sensor_name] = s.get_cadence(df)
        
        # find next acquisition time, if search time is today then returns 'N/A'
        if date == None:
            next_acq[sensor_name] = 'N/A'
            
        else:
            next_acq[sensor_name] = 'Time of next acquisition after ' + str(date[1]) + ' is ' + str(s.acq_search(sensor_name.lower(), aoi, date[1]))
        
        # find area intersection for each sensor
#         coords = [Polygon(c) for c in coords]
#         area[sensor_name] = unary_union([a.intersection(b) for a, b in combinations(coords, 2)])
        
        if len(results) == 0:
            area[sensor_name] = 0
        else:
            area[sensor_name] = df.geometry[0]
            
            if len(results) > 1:
                
                for i in range(len(df) - 1):
                    area[sensor_name] = area[sensor_name].intersection(df.geometry[i + 1])
    master = s.get_sensor_cadence(dataframes)

    return freq, next_acq, area, master