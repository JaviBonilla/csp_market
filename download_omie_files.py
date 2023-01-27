import os
from calendar import monthrange
from joblib import Parallel, delayed

# Example URL:
# https://www.omie.es/es/file-download?parents%5B0%5D=marginalpdbc&filename=marginalpdbc_20220307.1
filename_base = 'marginalpdbc_{}{}{}.{}'
url = 'https://www.omie.es/es/file-download?parents%5B0%5D=marginalpdbc&filename='

# SET MAX VALUES
year = 2022

# SET NUMBER OF PROCESSES
processes = 4

# Data folder
folder = f'../data/{year}'

# Max tries
maxTries = 5


def prepend_zero(value):
    if value < 10:
        return f'0{value}'
    return f'{value}'


def download_file(input_year, input_month, input_day):
    size = 0
    tries = 1
    filename = ''
    while size <= 0 and tries < maxTries:
        filename = filename_base.format(input_year, prepend_zero(input_month), prepend_zero(input_day), tries)
        tries += 1
        url_day = f'{url}{filename}'
        file_path = f'{folder}/{filename}'
        if not os.path.exists(file_path):
            command = f'curl "{url_day}" --output {file_path}'
            os.system(command)
        size = os.path.getsize(file_path)
        if size > 0:
            print(filename)
        else:
            os.remove(file_path)
            print(f'Filename empty {filename}')
    if size <= 0:
        print(f'Filename not found {filename}')
        exit(1)


# Create folder if it doest not exist
if not os.path.exists(folder):
    os.makedirs(folder)

# Download data
for month in range(1, 13):
    num_days = monthrange(year, month)[1]
    results = Parallel(n_jobs=processes)(delayed(download_file)(year, month, day) for day in range(1, num_days + 1))
