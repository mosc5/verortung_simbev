import Plots
import Utility
import pandas as pd
import numpy as np


def uc1_public_fast(
        fuel_stations, boundaries,
        amenities, traffic_data,
        region, region_key):

    uc_id = 'Use_Case_3_Public_Fast'
    radius = 900  # radius around fuel station for traffic acquisition

    anz_fuel_stations = len(fuel_stations)

    fuel_in_region_bool = pd.Series(fuel_stations.geometry.within(boundaries.geometry[region_key]), name='Bool')

    fuel_stations = fuel_stations.join(fuel_in_region_bool)

    # add empty column for Traffic
    data = np.zeros(anz_fuel_stations)
    traffic = pd.Series(data, name='traffic')
    fuel_stations = fuel_stations.join(traffic)

    # locate fuelstations in region
    fs = fuel_stations.loc[fuel_stations['Bool'] == 1]

    x = np.arange(0, len(fs))
    fs = fs.assign(INDEX=x)
    fs.set_index('INDEX', inplace=True)

    # Calculating distribution Weights for Fuel Stations
    circles = fs.buffer(radius)

    anz_fs = len(fs)

    # Loop for calculating weight by using the appr. daily Traffic around Fuel Station
    i = 0
    while i < anz_fs:
        # Trafficdata inside a radius of 900 around Fuel Station
        traffic_around_fs = pd.Series(traffic_data.geometry.within(circles.geometry.iloc[i]), name='Bool')
        traffic_bool = traffic_data.join(traffic_around_fs)
        traffic_around_fs_true = traffic_data.loc[traffic_bool['Bool'] == 1]
        traffic_sum = traffic_around_fs_true['dtv'].sum()
        fs.iloc[i, 4] = traffic_sum

        i += 1

    anz_fs = len(fs)

    # Distribution of Energy
    if anz_fs > 0:
        data = np.zeros(anz_fs,)
        energy_sum_per_fs = pd.Series(data, name='energysum')
        fs = fs.join(energy_sum_per_fs)

        load_power = amenities.iloc[:, 8]
        load_power.name = 'loadpower_hpc'
        load_power = pd.to_numeric(load_power)
        energy_sum = load_power*15/60  # Ladeleistung in Energie umwandeln

        energy_sum_overall = energy_sum.sum()
        print(energy_sum_overall, 'kWh got fastcharged in region ', region_key)

        # sort descending by traffic
        fs = fs.sort_values(by=['traffic'], ascending=False)
        fs['conversionfactor'] = fs['traffic'] / sum(fs['traffic'])

        fs['energysum'] = fs['conversionfactor'] * energy_sum_overall

    else:
        print('No fast charging possible, because no fuel station in the area!')
    if anz_fs != 0:
        Plots.plot_uc1(fs, region,
                       traffic_data, circles)

    x = np.arange(0, len(fs))
    fs = fs.assign(INDEX=x)
    fs.set_index('INDEX', inplace=True)

    col_select = ['geometry', 'traffic', 'energysum', 'conversionfactor']
    Utility.save(fs, uc_id, col_select)

    return fs


def uc2_public_slow(
        public, boundaries,
        amenities, poi,
        region, region_key):

    print('UC2')
    uc_id = 'Use_Case_3_Public_Slow'
    public_in_region_bool = pd.Series(public.geometry.within(boundaries.geometry[region_key]), name='Bool')
    public_in_region = public.join(public_in_region_bool)
    pir = public_in_region.loc[public_in_region['Bool'] == 1]   # pir = public in region

    anz_pir = len(pir)
    data = np.zeros(anz_pir, )
    es = pd.Series(data, name='energysum')
    pir = pir.join(es)
    # pir['energysum'] = np.zeros

    load_power = amenities.iloc[:, 6]
    load_power.name = 'chargepower_public'
    load_power = pd.to_numeric(load_power)
    energy_sum = load_power * 15 / 60  # Ladeleistung in Energie umwandeln

    energy_sum_overall = energy_sum.sum()
    print(energy_sum_overall, 'kWh got charged at public space in region', region_key)

    # distribution of energysum based on weight of poi

    anz_pir = len(pir)

    #print(pir['amenity'])
    #print(poi.loc['atm', 5])
    h = pir['amenity']
    pir['conversionfactor'] = np.nan

    print(anz_pir)
    i = 0
    while i <= anz_pir-1:
        pir.iloc[i, 7] = float(poi.loc[h[i], 5].replace(',', '.'))
        i += 1

    pir['energysum'] = pir['conversionfactor'] * energy_sum_overall / anz_pir
    print(pir)
    Plots.plot_uc2(pir, region)


def uc3_private_home(
        zensus, boundaries,
        amenities, region,
        region_key):

    uc_id = 'Use_Case_3_Private_Home'

    # zensus = zensus.to_crs(3035)

    home_in_region_bool = pd.Series(zensus.geometry.within(boundaries.geometry[region_key]), name='Bool')
    home_in_region = zensus.join(home_in_region_bool)
    hir = home_in_region.loc[home_in_region['Bool'] == 1]   # hir = home in region

    anz_wir = len(hir)
    data = np.zeros(anz_wir, )
    es = pd.Series(data, name='energysum')
    hir = hir.join(es)
    hir['energysum'] = np.nan

    load_power = amenities.iloc[:, 7]
    load_power.name = 'chargepower_home'
    load_power = pd.to_numeric(load_power)
    energy_sum = load_power * 15 / 60  # Ladeleistung in Energie umwandeln

    energy_sum_overall = energy_sum.sum()
    print(energy_sum_overall, 'kWh got charged at home in region', region_key)

    # distribution of energysum based on population in 100x100 area
    pop_in_area = sum(hir['population'])

    hir['conversionfactor'] = home_in_region['population'] / pop_in_area

    hir['energysum'] = energy_sum_overall * hir['conversionfactor']  # np.nan

    hir = hir.sort_values(by=['population'], ascending=False)

    print(hir)
    print('UC3')

    Plots.plot_uc3(hir, region)

    x = np.arange(0, len(hir))
    hir = hir.assign(INDEX=x)
    hir.set_index('INDEX', inplace=True)
    col_select = ['population', 'geom_point', 'geometry', 'energysum', 'conversionfactor']
    Utility.save(hir, uc_id, col_select)

    return zensus


def uc4_private_work():
    print('UC4')
