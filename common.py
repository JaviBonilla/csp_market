import locale
import calendar
import datetime

# Dataframe headers
HEADER_DATE = 'date'
HEADER_VALUE = 'value'

# CSV headers
HEADER_CSV_DATE = 'Date & time'
HEADER_CSV_SOLAR = ' "Solar field net power (MW)"'
HEADER_CSV_TURBINE = ' "Turbine electric power (MW)"'

# Colors
COLOR_PLOTLY_TRANSPARENT = 'rgba(0,0,0,0)'
COLOR_PRICE = '#1c6cc8'
COLOR_SOLAR = '#F1C40F'
COLOR_TURBINE = '#BA4A00'

link_style = '''
/* unvisited link */
a:link {
  color: #ff4b4b;
  text-decoration: none;
}

/* visited link */
a:visited {
  color: #ff4b4b;
  text-decoration: none;
}

/* mouse over link */
a:hover {
  color: #b03434;
  text-decoration: none;
}

/* selected link */
a:active {
  color: #b03434;
  text-decoration: none;
}
'''


def data_filename(year, month, day, su=1):
    str_month = f'0{month}' if month < 10 else month
    str_day = f'0{day}' if day < 10 else day
    return f'marginalpdbc_{year}{str_month}{str_day}.{su}'


def dataframe_file(year):
    return f'../dataframes/market_{year}.df'


def format_number(value, decimals=2):
    return locale.format_string(f'%.{decimals}f', value, grouping=True)


def format_unit(value, decimals=2, unit='€'):
    mod = ''
    if value > 1e6:
        mod = 'M'
        value /= 1e6
    elif value > 1e3:
        mod = 'k'
        value /= 1e3
    return locale.format_string(f'%.{decimals}f', value, grouping=True) + ' ' + mod + unit


def de_format_unit(value: str):
    e = value.split(' ')
    if len(e) <= 1:
        return float(value) if value != '-' else 100
    if 'k' in e[1]:
        return float(e[0]) * 1e3
    if 'M' in e[1]:
        return float(e[0]) * 1e6
    return float(e[0])


def comparison_energy(df, year, month1, month2, power):
    last_day = calendar.monthrange(year, month2)[1]
    return format_unit(
        df[(df[HEADER_CSV_DATE].dt.date >= datetime.date(year, month1, 1)) &
           (df[HEADER_CSV_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_CSV_TURBINE].sum()/power,
        unit='h')


def comparison_energy_percentage(df1, df2, year, month1, month2, power):
    last_day = calendar.monthrange(year, month2)[1]
    sum1 = df1[(df1[HEADER_CSV_DATE].dt.date >= datetime.date(year, month1, 1)) &
               (df1[HEADER_CSV_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_CSV_TURBINE].sum()/power
    sum2 = df2[(df2[HEADER_CSV_DATE].dt.date >= datetime.date(year, month1, 1)) &
               (df2[HEADER_CSV_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_CSV_TURBINE].sum()/power
    if sum1 >= sum2:
        return '-'
    return format_unit(- 100 + 100 * sum1 / sum2, unit='%')


def comparison_economic_percentage(df1, df2, df_money, year, month1, month2,):
    last_day = calendar.monthrange(year, month2)[1]
    sum1 = (df1[(df1[HEADER_CSV_DATE].dt.date >= datetime.date(year, month1, 1)) & (
             df1[HEADER_CSV_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_CSV_TURBINE] * 1 *
            df_money[(df_money[HEADER_DATE].dt.date >= datetime.date(year, month1, 1)) & (
                   df_money[HEADER_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_VALUE]).sum()
    sum2 = (df2[(df2[HEADER_CSV_DATE].dt.date >= datetime.date(year, month1, 1)) & (
             df2[HEADER_CSV_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_CSV_TURBINE] * 1 *
            df_money[(df_money[HEADER_DATE].dt.date >= datetime.date(year, month1, 1)) & (
                   df_money[HEADER_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_VALUE]).sum()
    if sum1 >= sum2:
        return '-'
    return format_unit(- 100 + 100 * sum1 / sum2, unit='%')


def comparison_datasets(df, df_money, year, month1, month2):
    last_day = calendar.monthrange(year, month2)[1]
    return format_unit(
        (df[(df[HEADER_CSV_DATE].dt.date >= datetime.date(year, month1, 1)) & (
             df[HEADER_CSV_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_CSV_TURBINE] * 1 *
         df_money[(df_money[HEADER_DATE].dt.date >= datetime.date(year, month1, 1)) & (
                   df_money[HEADER_DATE].dt.date <= datetime.date(year, month2, last_day))][HEADER_VALUE]
         ).sum())


def styled_link(text, link):
    return f'<a href="{link}">{text}</a>'
