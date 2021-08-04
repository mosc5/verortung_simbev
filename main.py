
import pandas as pd
import geopandas as gpd

import Use_Cases
import Utility

# afgsdgadfg
if __name__ == '__main__':
    # read geopackeges
    fuel_stations = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\fuel_stations.gpkg')

    anz_fs = len(fuel_stations)

    boundaries = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\boundaries.gpkg')

    boundaries.set_index('ags_0', inplace=True)     # AGS als Index des Dataframes setzen
    boundaries = boundaries.dissolve(by='ags_0')    # Zusammenfassen der Regionenn mit geleichem AGS
    boundaries = boundaries.to_crs(3035)

    traffic = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\berlin_verkehr.gpkg')
    traffic = traffic.to_crs(3035)  # transforme to reference Coordinate System

    zensus_data = Utility.einlesen_geo(
        r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\destatis_zensus_population_per_ha_filtered.gpkg')
    zensus_data = zensus_data.to_crs(3035)
    zensus = zensus_data.iloc[:, 2:5]

    public = Utility.einlesen_geo(r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\osm_poi_elia.gpkg')

    poi_data = Utility.load_csv(r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\2020-12-02_OSM_POI_Gewichtung.csv')
    poi = pd.DataFrame.from_dict(poi_data)
    poi.set_index(0, inplace=True)
    print(poi)

    am_data = Utility.load_csv(r'C:\Users\Jakob.Wegner\PYTHON\GEOSim\Data\RES_SimBEV\amenity.csv')
    amenities = pd.DataFrame.from_dict(am_data)

    anz_regions = len(boundaries)
    region_key = '11000000'     # 8-Stellige AGS Gemindeschlüssel im Format str
    region = boundaries.loc[region_key, 'geometry']
    region = gpd.GeoSeries(region)  # Formatieren in Geoseries, sonst Probleme beim Plotten



    # Use Case HPC
    #fs = Use_Cases.uc1_public_fast(fuel_stations, boundaries,
     #                              amenities, traffic,
     #                              region, region_key)
    #pl = Use_Cases.uc3_private_home(zensus, boundaries, amenities,
      #                              region, region_key)

    pu = Use_Cases.uc2_public_slow(public, boundaries, amenities, poi, region, region_key)
