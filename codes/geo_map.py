import matplotlib.pyplot as plt
import matplotlib.cm

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
import matplotlib.cm as cm

def draw_map(x,y):
    l_lon = -123.3116 
    r_lon = -122.9923
    u_lat = 49.3341
    l_lat = 49.1808


    fig, ax = plt.subplots(figsize=(20,20))
    m = Basemap(resolution='c',projection='merc',area_thresh = 0.1,
                lat_0=(u_lat-l_lat)/2, lon_0=(l_lon-r_lon)/2,
                llcrnrlon=l_lon, llcrnrlat=l_lat,urcrnrlon=r_lon, urcrnrlat=u_lat)
    
    x1, y1 = m(x,y)

    m.readshapefile('vancouver_canada_land_coast','vancouver',
        color='black',
        zorder=2)

    m.scatter(x1, y1,s=1,c='#F2BDBE',alpha=0.2,marker='.')
    plt.show()
    return