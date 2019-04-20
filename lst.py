from rasterio.plot import show
import rasterio as rio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import seaborn as sns
sns.set()

class MidpointNormalize(colors.Normalize):
   
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
       
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


normalize = lambda array: ((array - array.min())/(array.max() - array.min()))
get_mat_or_val = lambda y, i: (x[i] for x in y)

def get_index(green, red, nir, swir):

    print(green.shape[0], red.shape[0], nir.shape[0], swir.shape[0])
    logor = lambda x, y: np.logical_or(x>0, y>0)
    calc = lambda x, y, ch: np.where(ch, (x-y)/(x+y), 0)
    np.seterr(divide='ignore', invalid='ignore')
    
    ndvi = calc(nir, red, logor(nir, red))
    ndwi = calc(green, swir, logor(green, swir))
    ndbi = calc(swir, nir, logor(nir, swir))
    return (ndvi.mean(), ndwi.mean(), ndbi.mean())

def get_LST(thermal, sat_name):

    if sat_name == 7:
        ml = 6.7087E-02
        al = -0.06709
        l_max = 17.040
        l_min = 0.000
        qcal_max = 255
        qcal_min = 1
        k1 = 666.09
        k2 = 1282.71

    else:
        ml = 3.3420E-04
        al = 0.10000
        l_max = 22.00180
        l_min = 0.10033
        qcal_max = 65535
        qcal_min = 1
        k1 = 774.8853
        k2 = 1321.0789

    L_lambda = ml * thermal + al
    temp_cel = k2 / np.log(k1/L_lambda + 1) - 273.15
    return temp_cel

def show_corr(temp, l):

    dates, sat = list(get_mat_or_val(l, 6)), get_mat_or_val(l, 5)
    green, red, nir, swir = get_mat_or_val(l, 0), get_mat_or_val(l, 1), get_mat_or_val(l, 2), get_mat_or_val(l, 3)
    d = list(zip(green, red, nir, swir))
    ndvi, ndbi, ndwi = [], [], []
    for i in range(len(d)):
        g,r,n,s = d[i]
        print(dates[i])
        try:
            k = get_index(g,r,n,s)
            
            ndvi.append(k[0])
            ndwi.append(k[1])
            ndbi.append(k[2])
        except Exception as e:
            print(e)
            pass
    temp = [i.mean() for i in temp]
    print(temp, ndvi, ndwi, ndbi)
    ax = plt.subplot(131)
    ax.plot(temp, ndvi, marker = 'o')
    ax.set_title('LST vs NDVI')
    ax.grid(False)
    ax = plt.subplot(132)
    ax.plot(temp, ndwi, marker = 'o')
    ax.set_title('LST vs NDWI')
    ax.grid(False)
    ax = plt.subplot(133)
    ax.plot(temp, ndbi, marker = 'o')
    ax.set_title('LST vs NDBI')
    ax.grid(False)
    plt.show()


def calc_everything(l):

    dates, sat = get_mat_or_val(l, 6), get_mat_or_val(l, 5)
    therm = get_mat_or_val(l, 4)
    d = list(zip(therm, sat))
    LST_arr = [(t, v) for t, v in d]
    temp_cel_list = list(map(lambda x: get_LST(x[0], x[1]), LST_arr))
    return temp_cel_list
    
if __name__ == '__main__':

    k = int(input('No. of Images: '))
    l=[]
    print('Enter green, red, nir, swir, first thermal band image, landsat 7/8 and year for {} images'.format(k))
    l = [tuple(input().strip().split()) for i in range(k)]
    l = list(map(lambda x: (rio.open(x[0]).read(1), rio.open(x[1]).read(1), rio.open(x[2]).read(1),
                            rio.open(x[3]).read(1), rio.open(x[4]).read(1), int(x[5]), x[6]), l))
    l = list(map(lambda x: tuple([i.astype(float) for i in x[:5]]+[x[5], x[6]]), l))
    l = sorted(l, key = lambda x: x[6])
    temp = calc_everything(l)
    show_corr(temp, l)
    
'''
lsat/00/b2.tif lsat/00/b3.tif lsat/00/b4.tif lsat/00/b5.tif lsat/00/b6.tif 7 2000
lsat/15/b3.tif lsat/15/b4.tif lsat/15/b5.tif lsat/15/b6.tif lsat/15/b10.tif 8 2015
lsat/19/b3.tif lsat/19/b4.tif lsat/19/b5.tif lsat/19/b6.tif lsat/19/b10.tif 8 2019
'''
    


