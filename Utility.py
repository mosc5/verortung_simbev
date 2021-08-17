
import csv
import geopandas as gpd
import pandas as pd


def einlesen_geo(filename):

    data = gpd.read_file(filename)
    return data

# load data from csv


def load_csv(file, delimiter=';', is_num=False, is_dict=False):
    data = {} if is_dict else []
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        header = next(csv_reader)  # read header
        for row in csv_reader:
            # get entry (key) of row
            # key = row.pop(0)
            # convert values to numbers
            if is_num:
                row = [float(d) for d in row]
            # single value in row
            if len(row) == 1:
                row = row[0]
            # save values
            # if is_dict:
            #   data[key] = row
            else:
                data.append(row)
        data = pd.DataFrame(data, columns=header)
    return data


def save(data, uc, col_select):

    filename = 'output_geo_{}.csv'.format(uc)
    path = '{}'.format(filename)  # path = '{}\{}'.format(pathlib.Path().resolve(), filename)
    data.to_csv(path, sep=';', columns=col_select, decimal=',', index=True)
    print('saving {} successful'.format(uc))
