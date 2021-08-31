
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import configparser as cp

import Use_Cases
import Utility

if __name__ == '__main__':

    print('Starting Program for Distribution of Energy...')

    # read config file
    parser = cp.ConfigParser()
    parser.read(r'c:\Users\Jakob.Wegner\PYTHON\verortung_simbev\location_config.cfg')
    uc1_radius = int(parser.get('uc_params', 'uc1_radius'))
    print(uc1_radius)
    print(type(uc1_radius))
    uc4_weight_retail = float(parser.get('uc_params', 'uc4_weight_retail'))
    uc4_weight_commercial = float(parser.get('uc_params', 'uc4_weight_commercial'))
    uc4_weight_industrial = float(parser.get('uc_params', 'uc4_weight_industrial'))
    # num_of_regions = parser.get('region_mode', 'num_of_regions')

    # print('Conifg is set to mode:', mode)
    # if 'single' in mode:
    #     region_key = (parser.get('basic', 'region_key'))
    # elif 'multi' in mode:
    region_data = Utility.load_csv(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\regions.csv')
    region_key = ['']*len(region_data)
    i = 0
    while i < len(region_data):
        region_key[i] = region_data.loc[i, 'AGS']
        i += 1

    anz_regions = len(region_key)
    print('Number of Regions set:', anz_regions)
    print('AGS Region_Key is set to:', region_key)

    # read input data
    fuel_stations = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\fuel_stations.gpkg')
    anz_fs = len(fuel_stations)

    boundaries = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\boundaries.gpkg')

    boundaries.set_index('ags_0', inplace=True)     # AGS als Index des Dataframes setzen
    boundaries = boundaries.dissolve(by='ags_0')    # Zusammenfassen der Regionenn mit geleichem AGS
    boundaries = boundaries.to_crs(3035)

    traffic = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\berlin_verkehr.gpkg')
    traffic = traffic.to_crs(3035)  # transforme to reference Coordinate System

    zensus_data = Utility.einlesen_geo(
        r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\destatis_zensus_population_per_ha_filtered.gpkg')
    zensus_data = zensus_data.to_crs(3035)
    zensus = zensus_data.iloc[:, 2:5]

    public = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\osm_poi_elia.gpkg')

    poi_data = Utility.load_csv(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\2020-12-02_OSM_POI_Gewichtung.csv')
    poi = pd.DataFrame.from_dict(poi_data)

    work = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\landuse.gpkg')

    am_data = Utility.load_csv(r'C:\Users\Jakob.Wegner\PYTHON\verortung_simbev\Data\RES_SimBEV\amenity.csv')
    amenities = pd.DataFrame.from_dict(am_data)

    anz_regions = len(boundaries)

    # Start the Use Cases for areas in region_key
    i = 0
    while i < len(region_key):
        region = boundaries.loc[region_key[i], 'geometry']
        region = gpd.GeoSeries(region)  # format to geoseries, otherwise problems plotting

        # Start Use Cases
        fs = Use_Cases.uc1_public_fast(fuel_stations, boundaries,
                                       amenities, traffic,
                                       region, region_key[i], uc1_radius)

        pu = Use_Cases.uc2_public_slow(public, boundaries,
                                       amenities, poi,
                                       region, region_key[i])

        pl = Use_Cases.uc3_private_home(zensus, boundaries,
                                        amenities, region,
                                        region_key[i])

        pw = Use_Cases.uc4_private_work(work, boundaries,
                                        amenities, region,
                                        region_key[i], uc4_weight_retail,
                                        uc4_weight_commercial, uc4_weight_industrial)
        i += 1

    plt.show()
