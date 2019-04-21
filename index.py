import rasterio as rio
from rasterio.plot import show
#import rasterio.plot as plt #import show
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.style.use('seaborn-deep')


def index(b2, b1):

    logor = lambda x, y: np.logical_or(x>0, y>0)
    calc = lambda x, y, ch: np.where(ch, (x-y)/(x+y), 0)
    ind = calc(b1, b2, logor(b2, b1))
    return ind


def plot_hist(plot_percent, dates, d):

    d = list(d)
    for i in range(len(plot_percent)):
        plot_percent[i] = plot_percent[i][:-1]
    plot_percent = list(np.array(plot_percent).transpose())
    ind = np.arange(len(dates))
    #dates = list(map(lambda x: round(x, 2), dates))
    ax = plt.subplot()
    bottom = [0]*len(dates)
    for i in range(len(d)):
        p = list(plot_percent[i])
        ax.bar(ind, p, bottom = bottom, width = 0.35, label = d[i])
        bottom = [bottom[i]+p[i] for i in range(len(p))]
    
    ax.set_xticks(ind, minor=False)
    ax.set_xticklabels(dates)
    ax.set_title('Percent Area Cover for years {} \n'.format(', '.join(dates[:-1])+' and ' + dates[-1]))
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        if(height!=0.0):
            x, y = p.get_xy()
            ax.annotate(str(round(height,1))+'%', (p.get_x()+.05*width, p.get_y()+.4*height))
    plt.show()
        
            
            
def plot_diff_util(ind_arr, bands, dates, ch):

    normalize = lambda array: ((array - array.min())/(array.max() - array.min()))
    bandsn = []
    for band in bands:
        band = band[:3]
        t = list(map(lambda x: normalize(x), band))
        t[0], t[2] = t[2], t[0]
        t = tuple(t)
        bandsn.append(np.dstack(t))
    n = len(ind_arr)
    d = list(zip(ind_arr, bandsn))
    date_dict = dict(zip(dates, d))

    return date_dict


def calc_table(ind, x, y, d):

    k, v = np.unique(ind[:]<=1.0, return_counts = True)
    tot_area = dict(zip(k, v))
    x = 23.5
    y = 23.5
    tot_area = tot_area[True]*x*y
    area, perc = [], []

    for k, v in d.items():
        a, b = np.unique(ind[:]<=v, return_counts = True)
        ar = dict(zip(a, b))
        
        ar = ar.get(True, 0)*x*y
        
        if v==0:
            area.append(ar)
            perc.append((ar*100)/tot_area)
        else:
            p = abs(sum(area)-ar)
            area.append(p)
            perc.append((p*100)/tot_area)
            
    area, perc = map(lambda t: [round(i, 3) for i in t], [area, perc])
    
    area.append(round(tot_area, 3))
    perc.append(100)
    return (perc, area)

def diff_table(ind_arr, bands, dates, d):

    aggr = list(zip(ind_arr, bands))
    percent = []
    ar = []
    df_list = []
    l = []
    y = list(d.values())
    for v in range(len(d)):
        if v==0:
            l.append('<= '+str(y[v]))
        else:
            l.append(str(y[v-1])+' - '+str(y[v]))
    
    for ind, band in aggr:
        x, y = band[4], band[5]
        a, b = calc_table(ind, x, y, d)
        percent.append(a)
        ar.append(b)
        #df_list.append(b)
    print(ar)
    ar = list(np.array(ar).transpose())
    pr = list(np.array(percent).transpose())
    date = []
    for i in range(len(dates)):
        date.append(str(dates[i]))
        date.append('')
        
    df_dict = {'Year': date, '#': ['Area (in m2)' if i%2==0 else 'Percentage Cover' for i in range(len(date))]}
    i = 0
    for k, v in d.items():
        print(i)
        a, b = ar[i], pr[i]
        app = []
        for x in range(len(a)):
            app.append(str(a[x]))
            app.append(str(b[x])+"%")
        df_dict[k] = app
        i = i + 1
    last = ar[-1]
    date = []
    for i in range(len(last)):
        date.append(str(last[i]))
        date.append('100%')
    df_dict['Total Area'] = date
    dfres = pd.DataFrame(df_dict)
    
    dfres.to_excel('result.xlsx')
    return percent

        
def calc_diff(l, ch):

    bands = []
    years = []
    for i in range(len(l)):
        trans = l[i][0].transform
        years.append(l[i][4])
        bands.append([l[i][0].read(1), l[i][1].read(1),
                          l[i][2].read(1), l[i][3].read(1), trans[0], -trans[4]])

    
    
    if ch==1:
        ind_arr = [index(band[1], band[2]) for band in bands]
        d = {'No Vegetation': 0.0, 'Lowest Vegetation': 0.15, 'Low Vegetation': 0.3, 'Dense Vegetation': 0.6, 'Highest Vegetation': 1.0}
        percent = diff_table(ind_arr, bands, years, d)
        plot_hist(percent, years, d.keys())
        
    elif ch==2:
        ind_arr = [index(band[3], band[0]) for band in bands]
        d = {'No Water': 0.0, 'Lowest Water': 0.15, 'Less Water': 0.3, 'Dense Water': 0.6, 'Highest Water': 1.0}
        percent = diff_table(ind_arr, bands, years, d)
        plot_hist(percent, years, d.keys())
        
    else:
        ind_arr = [index(band[2], band[3]) for band in bands]
        d = {'No Built-Up': 0.0, 'Lowest Built-up': 0.15, 'Less Built-Up': 0.3, 'Dense Built-up': 0.6, 'Highest Built-up': 1.0}
        percent = diff_table(ind_arr, bands, years, d)
        plot_hist(percent, years, d.keys())
    
    date_dict = plot_diff_util(ind_arr, bands, years, ch)
    
    
    
    while 1:
        
        date = input('enter year to plot')
        ind, band = date_dict[date]
        mid = ind.mean()
        minx=np.nanmin(ind)
        maxx=np.nanmax(ind)
        
        ax = plt.subplot(121)
        ax.imshow(ind, cmap=colormap, vmin=minx, vmax=maxx)
        ax.set_title('YEAR: {}'.format(date))
        ax1 = plt.subplot(122)
        ax1.imshow(band)
        ax1.set_title('FCC YEAR: {}'.format(date))
        plt.show()
    
    


if __name__ == '__main__':

    ch = int(input('Choose Index:\n1. NDVI\n2. NDWI\n3. NDBI'))
    k = int(input('No. of Images: '))
    l=[]
    print('Enter green, red, nir and swir image and year for {} images'.format(k))
    l = [tuple(input().strip().split()) for i in range(k)]
    l = list(map(lambda x: (rio.open(x[0]), rio.open(x[1]), rio.open(x[2]), rio.open(x[3]), x[4]), l))
    l = sorted(l, key = lambda x:x[4])
    calc_diff(l, ch)

    
