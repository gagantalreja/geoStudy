from rasterio.plot import show
import rasterio as rio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import seaborn as sns


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

    #k1, k2 qcal, ml, al values acquired from landsat data
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
    

    


