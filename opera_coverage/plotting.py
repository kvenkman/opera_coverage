import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.crs import CRS
from shapely.geometry import Polygon
import contextily as cx

# returns filled-in plot or outline of dictionary of polygons, single polygon, or dataframe (no outline available) with world map underneath
def visual(area, aoi: Polygon, outline = False):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)
    
    if type(area) == dict:
        
        color = ['blue','green','red']
    
        for num,frame in enumerate(area.keys()):
            df = gpd.GeoDataFrame(geometry = [area[frame]],
                                  crs = CRS.from_epsg(4326))
            if not outline:
                df.plot(ax = ax, alpha = .3, color=color[num], legend = True)
            else:
                df.boundary.plot(ax = ax, color=color[num])
            
    elif type(area) == gpd.geodataframe.GeoDataFrame:
        
        area.plot(column='sensor', ax = ax, alpha = .3, legend=True)
        # if not outline:
        #     df_wm.plot(column='sensor', ax = ax, alpha = .3, legend=True)
        # else:
        #     df_wm.boundary.plot(column='sensor', ax = ax, legend=True)
        
    elif type(area) == Polygon:
        
        df = gpd.GeoDataFrame(geometry = [area],
                              crs = CRS.from_epsg(4326))
        if not outline:
            df.plot(ax = ax, alpha = .25)
        else:
            df.boundary.plot(ax = ax)
    
    aoi.plot(ax=ax)
    cx.add_basemap(ax, crs=area.crs, zoom = 10)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

# returns plot of intersection of all polygons in input dictionary
def find_overlap(area, outline = False) -> Polygon:
    
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
    return overlap

def heatmap(value, long_block, lat_block):
    fig, ax = plt.subplots()
    im = ax.imshow(value)

    # x_tick = 

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Acquisitions', rotation=-90, va="bottom")

    # Loop over data dimensions and create text annotations.
    for i in range(len(lat_block)- 1):
        for j in range(len(long_block) - 1):
            text = ax.text(j, i, value[i, j],
                        ha="center", va="center", color="w")

    ax.set_title("Global temporal coverage")
    fig.tight_layout()
    plt.show()