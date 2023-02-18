import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import os
from persiantext import PersianText
import jalali

# >>>>>>>>>> globals <<<<<<<<<<
__FONT__ = './resources/IRANSansWeb(FaNum).ttf'
__RENT_STR__ = 'اجاره'
__SELL_STR__ = 'فروش'
__OTHER_STR__ = 'سایر'
__BASE_YEAR__ = 1399

CITY_NAMES = {'isfahan':'اصفهان', 'mashhad':'مشهد', 'shiraz':'شیراز', 'tehran':'تهران', 'karaj':'کرج'}
# >>>>>>>>>> functions <<<<<<<<<<

def get_font_properties(fontsize=10):
    return fm.FontProperties(fname=__FONT__, size=fontsize)

def convert_persian_digits_to_latin(s):
    digits = {'۰':'0', '۱':'1', '۲':'2', '۳':'3', '۴':'4', '۵':'5', '۶':'6', '۷':'7', '۸':'8', '۹':'9'}
    if type(s) == str:
        for pd in digits.keys():
            s = s.replace(pd, digits[pd])
    return s

def reshape_axes_labels(ax, reshape_x=True, reshape_y=False, fontsize=10):
    fp = get_font_properties(fontsize=fontsize)
    if reshape_x:
        xt = ax.get_xticklabels()
        for t in xt:
            t.set_text(PersianText.reshape(t.get_text()))
            t.set_fontproperties(fp)
        ax.set_xticklabels(xt)
    if reshape_y:
        yt = ax.get_yticklabels()
        for t in yt:
            t.set_text(PersianText.reshape(t.get_text()))
            t.set_fontproperties(fp)
        ax.set_yticklabels(yt)
    return

def stacked_bar(stacked_group, x, data, title=None, grid_cell=None, figsize=None):
    agg = data.groupby(by=[stacked_group, x]).count().iloc[:,0]
    agg = agg.unstack().T.fillna(0)
    
    bottom = np.zeros(len(agg))
    if grid_cell:
        ax = plt.subplot(grid_cell)
    else:
        plt.figure(figsize=figsize)
        ax = plt.subplot()
    
    for col in agg.columns:
        ax.bar(agg.index, agg[col], label=col, bottom=bottom)
        bottom = bottom + np.array(agg[col])
        
    if title:
        ax.set_title(PersianText.reshape(title), fontproperties=get_font_properties(20), pad=10)
        
    reshaped_cols = [PersianText.reshape(col) for col in agg.columns]
    ax.legend(labels=reshaped_cols, prop=get_font_properties(15))
    ax.set_xticklabels(agg.index, rotation=45, horizontalalignment='right')
    reshape_axes_labels(ax, fontsize=13)
    return

def count_bar(values, title=None, xlabel=None, ylabel=None, grid_cell=None, figsize=None):
    if grid_cell:
        ax = plt.subplot(grid_cell)
    else:
        plt.figure(figsize=figsize)
        ax = plt.subplot()
    ax = sns.countplot(x=values)
    reshape_axes_labels(ax, fontsize=10)
    plt.xticks(rotation=45, horizontalalignment='right')
    if title:
        plt.title(PersianText.reshape(title), fontproperties=get_font_properties(20))
    if xlabel:
        plt.xlabel(PersianText.reshape(xlabel), fontproperties=get_font_properties(20))
    if ylabel:
        plt.ylabel(PersianText.reshape(ylabel), fontproperties=get_font_properties(20))
    return

def mean_bar(x, y, data, title=None, xlabel=None, ylabel=None, grid_cell=None, figsize=None):
    if grid_cell:
        ax = plt.subplot(grid_cell)
    else:
        plt.figure(figsize=figsize)
        ax = plt.subplot()        
    ax = sns.barplot(x=x, y=y, data=data, errwidth=0)
    reshape_axes_labels(ax, fontsize=10)
    plt.xticks(rotation=45, horizontalalignment='right')
    if title:
        plt.title(PersianText.reshape(title), fontproperties=get_font_properties(20))
    if xlabel:
        plt.xlabel(PersianText.reshape(xlabel), fontproperties=get_font_properties(20))
    if ylabel:
        plt.ylabel(PersianText.reshape(ylabel), fontproperties=get_font_properties(20))
    return

def swarm(x, y, data, hue=None, title=None, xlabel=None, ylabel=None, legend_title=None, grid_cell=None, figsize=None):
    if grid_cell:
        ax = plt.subplot(grid_cell)
    else:
        plt.figure(figsize=figsize)
        ax = plt.subplot()        
    ax = sns.swarmplot(x=x, y=y, data=data, hue=hue)
    reshape_axes_labels(ax, fontsize=10)
    plt.xticks(rotation=45, horizontalalignment='right')
    if title:
        plt.title(PersianText.reshape(title), fontproperties=get_font_properties(20))
    if xlabel:
        plt.xlabel(PersianText.reshape(xlabel), fontproperties=get_font_properties(20))
    if ylabel:
        plt.ylabel(PersianText.reshape(ylabel), fontproperties=get_font_properties(20))
    if legend_title:
        plt.legend(title=PersianText.reshape(legend_title), prop=get_font_properties(10))
    return

def heatmap(data, title=None, xlabel=None, ylabel=None, cbar_label='', grid_cell=None, figsize=None):
    if grid_cell:
        ax = plt.subplot(grid_cell)
    else:
        plt.figure(figsize=figsize)
        ax = plt.subplot()
    if cbar_label:
        cbar_label = PersianText.reshape(cbar_label)
    ax = sns.heatmap(data, cmap='tab20b_r', cbar_kws={'label':cbar_label})
    reshape_axes_labels(ax, reshape_y=True, fontsize=10)
    plt.xticks(rotation=45, horizontalalignment='right')
    if title:
        plt.title(PersianText.reshape(title), fontproperties=get_font_properties(20), pad=15)
    if xlabel:
        plt.xlabel(PersianText.reshape(xlabel), fontproperties=get_font_properties(20))
    if ylabel:
        plt.ylabel(PersianText.reshape(ylabel), fontproperties=get_font_properties(20))
    return

def prepare_datasets(posts_json_file, city_name_fa):
    df = pd.read_json(posts_json_file)

    filter_cols = ['post_id', 'get_date', 'post_date', 'main_category', 'sub_category',
                'دسته‌بندی', 'محل', 'متراژ', 'سال ساخت', 'تعداد اتاق', 'ودیعه',
                'اجاره', 'قیمت کل', 'قیمت هر متر']
    df = df[filter_cols]
    df.columns = ['post_id', 'get_date', 'post_date', 'main_category', 'sub_category',
                'category', 'location', 'area', 'build_year', 'rooms', 'mortgage', 'rent',
                'sell_price', 'sell_unit_price']

    df['area'] = df['area'].apply(lambda x: convert_persian_digits_to_latin(x))
    df['area'] = df['area'].apply(lambda x: x.replace(' متر', '') if type(x) == str else x)
    df['area'] = df['area'].apply(lambda x: x.replace('٫', '') if type(x) == str else x)
    df['area'] = df['area'].str.strip().astype('float')

    df['build_year'] = df['build_year'].apply(lambda x: convert_persian_digits_to_latin(x))
    df['build_year'] = df['build_year'].apply(lambda x: x.replace('قبل از ', '') if type(x) == str else x)
    df['build_year'] = df['build_year'].str.strip().astype('float').astype('Int16')
    df['age'] = __BASE_YEAR__ - df['build_year']
    df['age'] = df['age'].astype('float')

    CNAME = city_name_fa + '، '
    df['location'] = df['location'].apply(lambda x: x.replace(CNAME, '') if type(x) == str else x)

    df['main_category'] = df['main_category'].fillna('')

    df['ad_type'] = df['main_category'].apply(lambda x: __RENT_STR__ if __RENT_STR__ in x else __SELL_STR__ if __SELL_STR__ in x else __OTHER_STR__)

    rooms = {'بدون اتاق':'0',
            'یک':'1',
            'دو':'2',
            'سه':'3',
            'چهار':'4',
            'پنج یا بیشتر':'5'}
    for r in rooms.keys():
        df['rooms'] = df['rooms'].apply(lambda x: x.replace(r, rooms[r]) if type(x) == str else x)
    df['rooms'] = df['rooms'].str.strip().astype('float').astype('Int16')

    df['sell_price'] = df['sell_price'].apply(lambda x: convert_persian_digits_to_latin(x))
    df['sell_price'] = df['sell_price'].apply(lambda x: x.replace(' تومان', '') if type(x) == str else x)
    df['sell_price'] = df['sell_price'].apply(lambda x: x.replace('٫', '') if type(x) == str else x)
    df['sell_price'] = df['sell_price'].replace('توافقی', np.nan)
    df['sell_price'] = df['sell_price'].replace('مجانی', np.nan)
    df['sell_price'] = df['sell_price'].str.strip().astype('float')#.astype('Int64')

    df['sell_unit_price'] = df['sell_unit_price'].apply(lambda x: convert_persian_digits_to_latin(x))
    df['sell_unit_price'] = df['sell_unit_price'].apply(lambda x: x.replace(' تومان', '') if type(x) == str else x)
    df['sell_unit_price'] = df['sell_unit_price'].apply(lambda x: x.replace('٫', '') if type(x) == str else x)
    df['sell_unit_price'] = df['sell_unit_price'].replace('توافقی', np.nan)
    df['sell_unit_price'] = df['sell_unit_price'].replace('مجانی', np.nan)
    df['sell_unit_price'] = df['sell_unit_price'].str.strip().astype('float')#.astype('Int64')

    df['mortgage'] = df['mortgage'].apply(lambda x: convert_persian_digits_to_latin(x))
    df['mortgage'] = df['mortgage'].apply(lambda x: x.replace(' تومان', '') if type(x) == str else x)
    df['mortgage'] = df['mortgage'].apply(lambda x: x.replace('٫', '') if type(x) == str else x)
    df['mortgage'] = df['mortgage'].replace('توافقی', np.nan)
    df['mortgage'] = df['mortgage'].replace('مجانی', np.nan)
    df['mortgage'] = df['mortgage'].str.strip().astype('float')#.astype('Int64')

    df['rent'] = df['rent'].apply(lambda x: convert_persian_digits_to_latin(x))
    df['rent'] = df['rent'].apply(lambda x: x.replace(' تومان', '') if type(x) == str else x)
    df['rent'] = df['rent'].apply(lambda x: x.replace('٫', '') if type(x) == str else x)
    df['rent'] = df['rent'].replace('توافقی', np.nan)
    df['rent'] = df['rent'].replace('مجانی', np.nan)
    df['rent'] = df['rent'].str.strip().astype('float')#.astype('Int64')

    area_cat_labels = (
        'کمتر از ۱۰۰',
        'از ۱۰۰ تا ۲۰۰',
        'از ۲۰۰ تا ۳۰۰',
        'از ۳۰۰ تا ۴۰۰',
        'از ۴۰۰ تا ۵۰۰',
        'بیشتر از ۵۰۰')
    df['area_cat'] = pd.cut(df['area'], bins=(0, 100, 200, 300, 400, 500, np.inf), labels=area_cat_labels)

    age_cat_labels = (
        'کمتر از ۵',
        'از ۵ تا ۱۰',
        'از ۱۰ تا ۱۵',
        'از ۱۵ تا ۲۰',
        'از ۲۰ تا ۲۵',
        'از ۲۵ تا ۳۰',
        'بیشتر از ۳۰')
    df['age_cat'] = pd.cut(df['age'], bins=(-1, 5, 10, 15, 20, 25, 30, np.inf), labels=age_cat_labels)

    df2 = df[['location', 'sub_category', 'ad_type', 'age', 'rooms', 'area', 'sell_price', 'sell_unit_price', 'mortgage', 'rent', 'area_cat', 'age_cat']].copy()
    df2 = df2[(~df2['sell_price'].isnull()) | (~df2['sell_unit_price'].isnull()) | (~df2['mortgage'].isnull()) | (~df2['rent'].isnull())]

    # this is just for Isfahan
    suburbs = ['شاهین شهر', 'بهارستان', 'فولادشهر', 'خمینی شهر', 'شهرضا', 'مبارکه', 'زرین‌شهر', 'تیران', 'گز', 'میمه']
    for town in suburbs:
        df2 = df2[df2['location'] != town]

    df_sell = df2[df2['ad_type'] == __SELL_STR__].copy()
    del df_sell['mortgage']
    del df_sell['rent']
    df_sell = df_sell.dropna()

    sell_unit_price_cat_labels = (
        'کمتر از ۲ میلیون',
        'از ۲ تا ۴ میلیون',
        'از ۴ تا ۶ میلیون',
        'از ۶ تا ۸ میلیون',
        'از ۸ تا ۱۰ میلیون',
        'بیشتر از ۱۰ میلیون')
    df_sell['sell_unit_price_cat'] = pd.cut(df_sell['sell_unit_price'], bins=(0, 2000000, 4000000, 6000000, 8000000, 10000000, np.inf), labels=sell_unit_price_cat_labels)

    df_rent = df2[df2['ad_type'] == __RENT_STR__].copy()
    del df_rent['sell_price']
    del df_rent['sell_unit_price']
    df_rent['rent'] = df_rent['rent'].fillna(0)
    df_rent['mortgage'] = df_rent['mortgage'].fillna(0)
    df_rent['rent_unit_price'] = (0.03 * df_rent['mortgage'] + df_rent['rent']) / df_rent['area']
    df_rent['rent_unit_price'] = np.round(df_rent['rent_unit_price'])
    df_rent = df_rent.dropna()

    rent_unit_price_cat_labels = (
        'کمتر از ۲۵ هزار',
        'از ۲۵ تا ۵۰ هزار',
        'از ۵۰ تا ۷۵ هزار',
        'از ۷۵ تا ۱۰۰ هزار',
        'از ۱۰۰ تا ۲۰۰ هزار',
        'از ۲۰۰ تا ۳۰۰ هزار',
        'بیشتر از ۳۰۰ هزار',
    )
    df_rent['rent_unit_price_cat'] = pd.cut(df_rent['rent_unit_price'], bins=(-1, 25000, 50000, 75000, 100000, 200000, 300000, np.inf), labels=rent_unit_price_cat_labels)
    return df2, df_sell, df_rent

def overall_charts(data, title, chart_file):
    plt.figure(figsize=(20,25))
    the_grid = GridSpec(nrows=3, ncols=2, hspace=0.50, wspace=0.2)

    df_agg = data[['ad_type', 'sub_category']].groupby(by=['ad_type']).count()
    df_agg = df_agg.reset_index()
    df_agg['ad_type'] = df_agg['ad_type'].apply(lambda x: PersianText.reshape(x))
    df_agg.columns = [PersianText.reshape(c) for c in list(df_agg.columns)]
    df_agg = df_agg.fillna(0)
    plt.subplot(the_grid[0, 1])
    plt.pie(x=df_agg['sub_category'], autopct='%1.1f%%', pctdistance=0.5,
            shadow=True, textprops={'fontproperties':get_font_properties(20)}, labels=df_agg['ad_type'])
    plt.title(PersianText.reshape('نسبت فروش و اجاره'), fontproperties=get_font_properties(20))
    plt.legend(list(df_agg['ad_type']), prop=get_font_properties(15))

    df_agg = data[['ad_type', 'sub_category']].groupby(by=['sub_category']).count()
    df_agg = df_agg.reset_index()
    df_agg['sub_category'] = df_agg['sub_category'].apply(lambda x: PersianText.reshape(x))
    df_agg.columns = [PersianText.reshape(c) for c in list(df_agg.columns)]
    df_agg = df_agg.fillna(0)
    plt.subplot(the_grid[0, 0])
    plt.pie(x=df_agg['ad_type'], autopct='%1.1f%%', pctdistance=0.5,
            shadow=True, textprops={'fontproperties':get_font_properties(13)}, labels=df_agg['sub_category'])
    plt.title(PersianText.reshape('نسبت املاک در دسته‌بندی‌ها'), fontproperties=get_font_properties(20))
    plt.legend(list(df_agg['sub_category']), prop=get_font_properties(10), loc='upper left')

    stacked_bar(stacked_group='ad_type', x='sub_category', data=data, title='تعداد فروش و اجاره در دسته‌بندی‌ها', grid_cell=the_grid[1, 1])
    stacked_bar(stacked_group='ad_type', x='area_cat', data=data, title='تعداد فروش و اجاره برحسب متراژ', grid_cell=the_grid[1, 0])
    stacked_bar(stacked_group='ad_type', x='location', data=data, title='تعداد فروش و اجاره در محل‌ها', grid_cell=the_grid[2, 0:])

    plt.suptitle(PersianText.reshape(title), fontproperties=get_font_properties(40))
    plt.savefig(chart_file)
    return

def sell_charts(data, title, chart_file, max_unit_price=np.inf):
    plt.figure(figsize=(20,35))
    the_grid = GridSpec(nrows=5, ncols=3, hspace=0.60, wspace=0.20)

    count_bar(values=data['area_cat'], grid_cell=the_grid[0, 2],
            title='تعداد بر حسب متراژ', xlabel='متراژ', ylabel='تعداد')
    mean_bar(x='area_cat', y='sell_unit_price', data=data, grid_cell=the_grid[0, 1],
            title='میانگین قیمت بر حسب متراژ', xlabel='متراژ', ylabel='میانگین (۱۰ میلیون تومان)')
    mean_bar(x='area_cat', y='age', data=data, grid_cell=the_grid[0, 0],
            title='میانگین سن بر حسب متراژ', xlabel='متراژ', ylabel='میانگین (سال)')

    count_bar(values=data['age_cat'], grid_cell=the_grid[1, 2],
            title='تعداد بر حسب سن', xlabel='سن بنا', ylabel='تعداد')
    mean_bar(x='age_cat', y='sell_unit_price', data=data, grid_cell=the_grid[1, 1],
            title='میانگین قیمت بر حسب سن', xlabel='سن بنا', ylabel='میانگین (۱۰ میلیون تومان)')
    mean_bar(x='age_cat', y='area', data=data, grid_cell=the_grid[1, 0],
            title='میانگین متراژ بر حسب سن', xlabel='سن بنا', ylabel='میانگین (مترمربع)')

    count_bar(values=data['sell_unit_price_cat'], grid_cell=the_grid[2, 2],
            title='تعداد بر حسب قیمت', xlabel='قیمت هر متر', ylabel='تعداد')
    mean_bar(x='sell_unit_price_cat', y='age', data=data, grid_cell=the_grid[2, 1],
            title='میانگین سن بر حسب قیمت', xlabel='قیمت هر متر', ylabel='میانگین (سال)')
    mean_bar(x='sell_unit_price_cat', y='area', data=data, grid_cell=the_grid[2, 0],
            title='میانگین متراژ بر حسب قیمت', xlabel='قیمت هر متر', ylabel='میانگین (مترمربع)')

    df_temp = data[data['sell_unit_price'] <= max_unit_price]
    df_agg = df_temp[['location', 'age_cat', 'sell_unit_price']]
    df_agg = df_agg.groupby(by=['age_cat', 'location']).mean()
    df_agg = df_agg.unstack()
    df_agg.columns = df_agg.columns.get_level_values(1)
    heatmap(data=df_agg, title='میانگین قیمت هر متر به نسبت محل و سن', xlabel='محل', ylabel='سن (سال)', cbar_label='۱۰ میلیون', grid_cell=the_grid[3, 0:])

    df_temp = data[data['sell_unit_price'] <= max_unit_price]
    swarm(x='area_cat', y='sell_unit_price', hue='rooms', data=df_temp, grid_cell=the_grid[4, 0:],
        title='تعداد برحسب متراژ، قیمت و تعداد اتاق', xlabel='متراژ', ylabel='قیمت هر متر (۱۰ میلیون تومان)',
        legend_title='تعداد اتاق')

    plt.suptitle(PersianText.reshape(title), fontproperties=get_font_properties(40))
    plt.savefig(chart_file)
    return

def rent_charts(data, title, chart_file, max_unit_rent=np.inf):
    plt.figure(figsize=(20,35))
    the_grid = GridSpec(nrows=5, ncols=3, hspace=0.50, wspace=0.3)

    count_bar(values=data['area_cat'], grid_cell=the_grid[0, 2],
            title='تعداد بر حسب متراژ', xlabel='متراژ', ylabel='تعداد')
    mean_bar(x='area_cat', y='rent_unit_price', data=data, grid_cell=the_grid[0, 1],
            title='میانگین اجاره بر حسب متراژ', xlabel='متراژ', ylabel='میانگین')
    mean_bar(x='area_cat', y='age', data=data, grid_cell=the_grid[0, 0],
            title='میانگین سن بر حسب متراژ', xlabel='متراژ', ylabel='میانگین (سال)')

    count_bar(values=data['age_cat'], grid_cell=the_grid[1, 2],
            title='تعداد بر حسب سن', xlabel='سن بنا', ylabel='تعداد')
    mean_bar(x='age_cat', y='rent_unit_price', data=data, grid_cell=the_grid[1, 1],
            title='میانگین اجاره بر حسب سن', xlabel='سن بنا', ylabel='میانگین')
    mean_bar(x='age_cat', y='area', data=data, grid_cell=the_grid[1, 0],
            title='میانگین متراژ بر حسب سن', xlabel='سن بنا', ylabel='میانگین (مترمربع)')

    count_bar(values=data['rent_unit_price_cat'], grid_cell=the_grid[2, 2],
            title='تعداد بر حسب اجاره', xlabel='اجاره به ازای هر متر', ylabel='تعداد')
    mean_bar(x='rent_unit_price_cat', y='age', data=data, grid_cell=the_grid[2, 1],
            title='میانگین سن بر حسب اجاره', xlabel='اجاره به ازای هر متر', ylabel='میانگین (سال)')
    mean_bar(x='rent_unit_price_cat', y='area', data=data, grid_cell=the_grid[2, 0],
            title='میانگین متراژ بر حسب اجاره', xlabel='اجاره به ازای هر متر', ylabel='میانگین (مترمربع)')

    df_temp = data[data['rent_unit_price'] <= max_unit_rent]
    df_agg = df_temp[['location', 'age_cat', 'rent_unit_price']]
    df_agg = df_agg.groupby(by=['age_cat', 'location']).mean()
    df_agg = df_agg.unstack()
    df_agg.columns = df_agg.columns.get_level_values(1)
    heatmap(data=df_agg, title='میانگین اجاره هر متر به نسبت محل و سن', xlabel='محل', ylabel='سن (سال)', cbar_label='', grid_cell=the_grid[3, 0:])

    df_temp = data[data['rent_unit_price'] <= max_unit_rent]
    swarm(x='area_cat', y='rent_unit_price', hue='rooms', data=df_temp, grid_cell=the_grid[4, 0:],
        title='تعداد برحسب متراژ، اجاره و تعداد اتاق', xlabel='متراژ', ylabel='اجاره به ازای هر متر',
        legend_title='تعداد اتاق')

    plt.suptitle(PersianText.reshape(title), fontproperties=get_font_properties(40))
    plt.savefig(chart_file)
    return

# >>>>>>>>> main <<<<<<<<<<
if __name__ == "__main__":
    gd = str(datetime.now().date())
    jd = jalali.Gregorian(gd).persian_string(date_format='{}{:02d}{:02d}')
    # jd = '13990324'

    city_name_en = 'isfahan'
    raw_data = './data/{}--real-estate--{}.json'.format(city_name_en, jd)
    if os.path.exists(raw_data):
        print('** Preparing data ...')
        df_total, df_sell, df_rent = prepare_datasets(raw_data, city_name_fa=CITY_NAMES[city_name_en])
    else:
        print('***** ERROR:', raw_data, 'NOT FOUND!')
        exit(0)

    df_sell_apartment = df_sell[df_sell['sub_category'] == 'آپارتمان']
    df_sell_house = df_sell[df_sell['sub_category'] == 'خانه و ویلا']
    df_rent_apartment = df_rent[df_rent['sub_category'] == 'آپارتمان']
    df_rent_house = df_rent[df_rent['sub_category'] == 'خانه و ویلا']

    print('** Visualizing data ...')

    title = 'نمای کلی آگهی‌های املاک {}'.format(CITY_NAMES[city_name_en])
    chart_file = './charts/{}--overall-{}.png'.format(city_name_en, jd)
    overall_charts(df_total, title=title, chart_file=chart_file)

    chart_file = './charts/{}--apartment-sell--{}.png'.format(city_name_en, jd)
    sell_charts(df_sell_apartment, title='نمای آپارتمان‌های فروشی', chart_file=chart_file, max_unit_price=5e7)
    chart_file = './charts/{}--apartment-rent--{}.png'.format(city_name_en, jd)
    rent_charts(df_rent_apartment, title='نمای آپارتمان‌های اجاره‌ای', chart_file=chart_file, max_unit_rent=200000)

    chart_file = './charts/{}--house-sell--{}.png'.format(city_name_en, jd)
    sell_charts(df_sell_house, title='نمای خانه‌های فروشی', chart_file=chart_file, max_unit_price=5e7)
    chart_file = './charts/{}--house-rent--{}.png'.format(city_name_en, jd)
    rent_charts(df_rent_house, title='نمای خانه‌های اجاره‌ای', chart_file=chart_file, max_unit_rent=200000)
