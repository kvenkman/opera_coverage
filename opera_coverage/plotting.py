import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.crs import CRS
from shapely.geometry import Polygon
import contextily as cx

# returns filled-in plot or outline of dictionary of polygons (or single polygon) with world map underneath
def visual(area, outline = False):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)
    
    if type(area) == dict:
        
        color = ['blue','green','red']
    
        for num,frame in enumerate(area.keys()):
            df = gpd.GeoDataFrame(geometry = [area[frame]],
                                  crs = CRS.from_epsg(4326))
            df_wm = df.to_crs(epsg = 3857)
            if not outline:
                df_wm.plot(ax = ax, alpha = .3, color=color[num], legend = True)
            else:
                df_wm.boundary.plot(ax = ax, color=color[num])
            
    elif type(area) == gpd.GeoSeries:
        
        df_wm = area.to_crs(epsg = 3857)
        if not outline:
            df_wm.plot(ax = ax, alpha = .3)
        else:
            df_wm.boundary.plot(ax = ax)
        
    elif type(area) == Polygon:
        
        df = gpd.GeoDataFrame(geometry = [area],
                              crs = CRS.from_epsg(4326))
        df_wm = df.to_crs(epsg = 3857)
        if not outline:
            df_wm.plot(ax = ax, alpha = .3)
        else:
            df_wm.boundary.plot(ax = ax)
    
    cx.add_basemap(ax, zoom = 10)

# returns plot of intersection of all polygons in input dictionary
def find_overlap(area, outline = False):
    
    if type(area) == dict:
        for idx,key in enumerate(area.keys()):
            if idx == 0:
                overlap = area[key]
            else:
                overlap = overlap.intersection(area[key])
    elif type(area) == gpd.GeoSeries:
        overlap = area[0]
        if len(area) > 1:
            for i in range(len(area) - 1):
                overlap = overlap.intersection(area[i + 1])
            
    visual(overlap, outline)