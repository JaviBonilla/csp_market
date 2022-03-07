from os import path
import common
import pandas as pd
from calendar import monthrange
from datetime import timedelta

# Data from OMIE - Mercado diario
# https://www.omie.es/es/file-access-list


def csv_to_data(file, data):
    df_csv = pd.read_csv(file, sep=';', skiprows=1, skipfooter=1, header=None, engine='python', verbose=False)
    for index, row in df_csv.iterrows():
        year = int(row[0])
        month = int(row[1])
        day = int(row[2])
        hour = int(row[3])
        value = row[4]
        # WARNING: ignore hour == 25 when the hour is changed (Ex: 2019-10-27)
        if hour > 24:
            continue
        if hour < 24:
            date = pd.to_datetime(f'{year}-{month}-{day} {hour}:00:00', utc=True)
        else:
            date = pd.to_datetime(f'{year}-{month}-{day} {hour-1}:00:00', utc=True)
            date = date + timedelta(hours=1)
        data.append([date, value])
    return data


# Main function
def main(year):

    # Data folder
    folder = f'../data/{year}/'

    # Data from files
    data = []

    # Iterate over files
    for month in range(1, 13):
        _, last = monthrange(year, month)
        for day in range(1, last+1):
            filename = common.data_filename(year, month, day, su=1)
            file = f'{folder}{filename}'
            exists = True
            if not path.exists(file):
                filename = common.data_filename(year, month, day, su=2)
                file = f'{folder}{filename}'
                if not path.exists(file):
                    exists = False
            if exists:
                data = csv_to_data(file, data)

    # Create dataframe and save to file
    df = pd.DataFrame(data, columns=[common.HEADER_DATE, common.HEADER_VALUE])
    df.to_pickle(common.dataframe_file(year), protocol=4)


if __name__ == '__main__':
    main(year=2022)
