import common
import datetime
import pandas as pd
import streamlit as st
import plotly.graph_objs as go

# Available years
years = (2019, 2020, 2021, 2022)
default_year = 2

# PlotLy font size
figure_font_size = 16

# CSV files
csv_ns = './csv/csp_data_NS.csv'
csv_ew = './csv/csp_data_EW.csv'

# PTC plant power
ptc_installed_power = 50

# Hover configuration
hover_mode = 'closest'
hover_label = dict(bgcolor="black", font_size=13.5)
solar_hover_template = '<br><b>Date</b>: %{x}<br>' + '<b>Production</b>: %{y:,.2f} MW' + '<extra></extra>'
turbine_hover_template = '<br><b>Date</b>: %{x}<br>' + '<b>Production</b>: %{y:,.2f} MW' + '<extra></extra>'
price_hover_template = '<br><b>Date</b>: %{x}<br>' + '<b>Price</b>: %{y:,.2f} €/MWh' + '<extra></extra>'


@st.cache_data
def load_dataframe(year):
    # Load from file
    df = pd.read_pickle(common.dataframe_file(year))

    # Convert from €/MWh to c€/kWh
    # df[common.HEADER_VALUE] = df[common.HEADER_VALUE].apply(lambda value: value / 10)

    # Load from CSV
    df_ns = pd.read_csv(csv_ns)
    df_ew = pd.read_csv(csv_ew)

    # Replace year
    df_ns[common.HEADER_CSV_DATE] = df_ns[common.HEADER_CSV_DATE].apply(lambda value: value.replace('2021', str(year)))
    df_ew[common.HEADER_CSV_DATE] = df_ew[common.HEADER_CSV_DATE].apply(lambda value: value.replace('2021', str(year)))

    # Convert to date time
    df_ns[common.HEADER_CSV_DATE] = pd.to_datetime(df_ns[common.HEADER_CSV_DATE], format='%Y-%m-%d %H:%M:%S')
    df_ew[common.HEADER_CSV_DATE] = pd.to_datetime(df_ew[common.HEADER_CSV_DATE], format='%Y-%m-%d %H:%M:%S')

    # Fix values
    df_ns[common.HEADER_CSV_SOLAR] = \
        df_ns[common.HEADER_CSV_SOLAR].apply(lambda value: float(value.replace('"', '').strip()))
    df_ns[common.HEADER_CSV_TURBINE] = \
        df_ns[common.HEADER_CSV_TURBINE].apply(lambda value: float(value.replace('"', '').strip()))
    df_ew[common.HEADER_CSV_SOLAR] = \
        df_ew[common.HEADER_CSV_SOLAR].apply(lambda value: float(value.replace('"', '').strip()))
    df_ew[common.HEADER_CSV_TURBINE] = \
        df_ew[common.HEADER_CSV_TURBINE].apply(lambda value: float(value.replace('"', '').strip()))

    # Ignore negative values
    df_ns[common.HEADER_CSV_SOLAR] = \
        df_ns[common.HEADER_CSV_SOLAR].apply(lambda value: max(0, value))
    df_ns[common.HEADER_CSV_TURBINE] = \
        df_ns[common.HEADER_CSV_TURBINE].apply(lambda value: max(0, value))
    df_ew[common.HEADER_CSV_SOLAR] = \
        df_ew[common.HEADER_CSV_SOLAR].apply(lambda value: max(0, value))
    df_ew[common.HEADER_CSV_TURBINE] = \
        df_ew[common.HEADER_CSV_TURBINE].apply(lambda value: max(0, value))

    return df, df_ns, df_ew


def configuration(max_width: int = 1000):
    st.set_page_config(
        page_title='Economic comparison between PTC orientations',
        page_icon=':sunrise_over_mountains:',
        initial_sidebar_state='expanded',
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': 'Economic comparison between PTC orientations.'
        }
    )
    max_width_str = f"max-width: {max_width}px;"
    st.markdown(f""" 
                <style> 
                .block-container{{{max_width_str}}}
                .css-qrbaxs{{display: none;}}
                {common.link_style}
                </style>    
                """,
                unsafe_allow_html=True)


def df_style(s):
    color = 'rgba(255, 255, 0, 0.2);'
    col1 = color if s[0] != '-' and common.de_format_unit(s[0]) > common.de_format_unit(s[1]) else ''
    col2 = color if s[1] != '-' and common.de_format_unit(s[1]) > common.de_format_unit(s[0]) else ''
    return [f'background-color: {col1}', f'background-color: {col2}']


def dashboard():

    # Side bar
    st.sidebar.markdown('## Year')
    year = st.sidebar.radio(' ', years, index=default_year)
    st.sidebar.markdown('## Sections')
    st.sidebar.markdown(common.styled_link('Spanish Power Market Auction', '#spanish-power-market-auction'),
                        unsafe_allow_html=True)
    st.sidebar.markdown(common.styled_link('Power Plant and Simulation Description', '#power-plant-and-simulation-description'),
                        unsafe_allow_html=True)
    st.sidebar.markdown(common.styled_link('Solar Field Net Production', '#solar-field-net-production'),
                        unsafe_allow_html=True)
    st.sidebar.markdown(common.styled_link('Turbine Electric Power', '#turbine-electric-power'),
                        unsafe_allow_html=True)
    st.sidebar.markdown(common.styled_link('Earnings', '#earnings'),
                        unsafe_allow_html=True)
    st.sidebar.markdown(common.styled_link('Comparison per Month', '#energy-comparison-per-month'),
                        unsafe_allow_html=True)

    # Body
    st.title(f'Economic comparison between PTC orientations')
    st.markdown(f'#### **Considered year:** {year}')
    st.header('')
    st.header('Date interval')
    year_first = datetime.date(year, 1, 1)
    year_last = datetime.date(year, 12, 31)
    col1, col2 = st.columns(2)
    first_date = col1.date_input('From', value=year_first, min_value=year_first, max_value=year_last, key=None)
    last_date = col2.date_input('To', value=year_last, min_value=year_first, max_value=year_last, key=None)

    # Dataframe
    df, df_ns, df_ew = load_dataframe(year)

    # Filter by date
    df = df[(df[common.HEADER_DATE].dt.date >= first_date) & (df[common.HEADER_DATE].dt.date <= last_date)]
    df_ns = df_ns[(df_ns[common.HEADER_CSV_DATE].dt.date >= first_date) &
                  (df_ns[common.HEADER_CSV_DATE].dt.date <= last_date)]
    df_ew = df_ew[(df_ew[common.HEADER_CSV_DATE].dt.date >= first_date) &
                  (df_ew[common.HEADER_CSV_DATE].dt.date <= last_date)]

    # Average price
    value_len = len(df[common.HEADER_VALUE])
    value_sum = sum(df[common.HEADER_VALUE])
    avg_price = value_sum / value_len if value_len > 0 else 0

    # Market
    st.subheader('')
    st.header('Spanish Power Market Auction')
    price = go.Scatter(x=df[common.HEADER_DATE], y=df[common.HEADER_VALUE], name='Price',
                       mode='lines', line=dict(width=2, color=common.COLOR_PRICE), fill='tozeroy',
                       fillcolor=common.COLOR_PRICE,
                       hovertemplate=price_hover_template)
    layout_price = go.Layout(xaxis=dict(title=''),
                             yaxis=dict(title='Price', tickformat='0,000.00f', hoverformat=',.2f',
                                        ticksuffix=' €/MWh', separatethousands=True),
                             hoverlabel=dict(font=dict(color='white'))
                             )
    fig_price = go.Figure(data=[price], layout=layout_price)
    fig_price.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    st.plotly_chart(fig_price, use_container_width=True)
    st.markdown('Data from [OMIE]'
                '(https://www.omie.es/es/file-access-list#Mercado%20Diario1.%20Precios?parent=Mercado%20Diario)')
    st.markdown(f'Average price: **{common.format_number(avg_price)} €/MWh**')

    st.header('Power Plant and Simulation Description')
    st.markdown('''
    - **Facility:** Parabolic-Trough Collector (PTC) Solar Thermal Power Plant
        - **Power:** 50 MW
        - **Thermal storage:** 8 hours
    - **Data:** Typical Meteorological Year (TMY)
        - **Location:** Almería, Spain
        - **Source:** [PVGIS](https://ec.europa.eu/jrc/en/pvgis)
    - **Operation:** Continuously dispatch 
    - **Simulator:** [PTC Power Plant Performance](https://ptc-performance.web.app/)    
    ''')
    st.header('Results')
    # ---------------------
    # North-south PTC plant
    # ---------------------
    col_ns, col_ew = st.columns([0.5, 0.5])
    col_ns.header('North-south')
    col_ns.subheader('')

    # Solar production
    col_ns.subheader('Solar field net production')
    csp_ns = go.Scatter(x=df_ns[common.HEADER_CSV_DATE], y=df_ns[common.HEADER_CSV_SOLAR], name='Solar field',
                        mode='lines', line=dict(width=2, color=common.COLOR_SOLAR), fill='tozeroy',
                        fillcolor=common.COLOR_SOLAR,
                        hovertemplate=solar_hover_template)
    layout_csp_ns = go.Layout(xaxis=dict(title=''), yaxis=dict(title='Solar field net power', tickformat='0,000.00f',
                                                               hoverformat=',.2f', ticksuffix=' MW',
                                                               separatethousands=True),
                              hoverlabel=dict(font=dict(color='white')))
    fig_csp_ns = go.Figure(data=[csp_ns], layout=layout_csp_ns)
    fig_csp_ns.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    col_ns.plotly_chart(fig_csp_ns, use_container_width=True)

    # Turbine production
    col_ns.subheader('Turbine electric power')
    power_ns = go.Scatter(x=df_ns[common.HEADER_CSV_DATE], y=df_ns[common.HEADER_CSV_TURBINE], name='Turbine',
                          mode='lines', line=dict(width=2, color=common.COLOR_TURBINE), fill='tozeroy',
                          fillcolor=common.COLOR_TURBINE,
                          hovertemplate=turbine_hover_template)
    layout_power_ns = go.Layout(xaxis=dict(title=''), yaxis=dict(title='Turbine power', tickformat='0,000.00f',
                                                                 hoverformat=',.2f', ticksuffix=' MW',
                                                                 separatethousands=True),
                                hoverlabel=dict(font=dict(color='white')))
    fig_power_ns = go.Figure(data=[power_ns], layout=layout_power_ns)
    fig_power_ns.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    col_ns.plotly_chart(fig_power_ns, use_container_width=True)
    col_ns.markdown('Equivalent hours: **'
                    f'{common.format_unit(df_ns[common.HEADER_CSV_TURBINE].sum()/ptc_installed_power, unit="h")}**')

    # Earnings
    col_ns.subheader('Earnings')
    earnings_ns = df_ns[common.HEADER_CSV_TURBINE] * df[common.HEADER_VALUE]
    power_ns = go.Scatter(x=df_ns[common.HEADER_CSV_DATE], y=earnings_ns,
                          name='Earnings', mode='lines', line=dict(width=2, color=common.COLOR_PRICE), fill='tozeroy',
                          fillcolor=common.COLOR_PRICE, hovertemplate=price_hover_template)
    layout_earnings_ns = go.Layout(xaxis=dict(title=''), yaxis=dict(title='Earnings', tickformat='0,000.00f',
                                                                    hoverformat=',.2f', ticksuffix=' €',
                                                                    separatethousands=True),
                                   hoverlabel=dict(font=dict(color='white')))
    fig_power_ns = go.Figure(data=[power_ns], layout=layout_earnings_ns)
    fig_power_ns.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    col_ns.plotly_chart(fig_power_ns, use_container_width=True)
    col_ns.markdown(f'Total earnings: **{common.format_unit(earnings_ns.sum())}**')

    # ---------------------
    # East-west PTC plant
    # ---------------------
    col_ew.header('East-west')
    col_ew.title('')

    # Solar production
    col_ew.subheader('Solar field net production')
    csp_ew = go.Scatter(x=df_ew[common.HEADER_CSV_DATE], y=df_ew[common.HEADER_CSV_SOLAR], name='Solar field',
                        mode='lines', line=dict(width=2, color=common.COLOR_SOLAR), fill='tozeroy',
                        fillcolor=common.COLOR_SOLAR,
                        hovertemplate=solar_hover_template)
    fig_csp_ew = go.Figure(data=[csp_ew], layout=layout_csp_ns)
    fig_csp_ew.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    col_ew.plotly_chart(fig_csp_ew, use_container_width=True)

    # Turbine production
    col_ew.subheader('Turbine electric power')
    power_ew = go.Scatter(x=df_ew[common.HEADER_CSV_DATE], y=df_ew[common.HEADER_CSV_TURBINE], name='Turbine',
                          mode='lines', line=dict(width=2, color=common.COLOR_TURBINE), fill='tozeroy',
                          fillcolor=common.COLOR_TURBINE, hovertemplate=turbine_hover_template)
    fig_power_ew = go.Figure(data=[power_ew], layout=layout_power_ns)
    fig_power_ew.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    col_ew.plotly_chart(fig_power_ew, use_container_width=True)
    col_ew.markdown('Equivalent hours: **'
                f'{common.format_unit(df_ew[common.HEADER_CSV_TURBINE].sum()/ptc_installed_power, unit="h")}**')

    # Earnings
    col_ew.subheader('Earnings')
    earnings_ew = df_ew[common.HEADER_CSV_TURBINE] * df[common.HEADER_VALUE]
    power_ew = go.Scatter(x=df_ew[common.HEADER_CSV_DATE], y=earnings_ew,
                          name='Earnings', mode='lines', line=dict(width=2, color=common.COLOR_PRICE), fill='tozeroy',
                          fillcolor=common.COLOR_PRICE,
                          hovertemplate=price_hover_template)
    fig_power_ns = go.Figure(data=[power_ew], layout=layout_earnings_ns)
    fig_power_ns.update_layout(font_size=figure_font_size, hovermode=hover_mode,  hoverlabel=hover_label)
    col_ew.plotly_chart(fig_power_ns, use_container_width=True)
    col_ew.markdown(f'Total earnings: **{common.format_unit(earnings_ew.sum())}**')

    # Comparison
    col_comp1, col_comp2 = st.columns([0.5, 0.5])

    col_comp1.subheader('Energy comparison per month')
    data = {
        'Jan': [
            common.comparison_energy(df_ns, year, 1, 1, ptc_installed_power),
            common.comparison_energy(df_ew, year, 1, 1, ptc_installed_power)
        ],
        'Feb': [
            common.comparison_energy(df_ns, year, 2, 2, ptc_installed_power),
            common.comparison_energy(df_ew, year, 2, 2, ptc_installed_power)
        ],
        'Mar': [
            common.comparison_energy(df_ns, year, 3, 3, ptc_installed_power),
            common.comparison_energy(df_ew, year, 3, 3, ptc_installed_power)
        ],
        'Apr': [
            common.comparison_energy(df_ns, year, 4, 4, ptc_installed_power),
            common.comparison_energy(df_ew, year, 4, 4, ptc_installed_power)
        ],
        'May': [
            common.comparison_energy(df_ns, year, 5, 5, ptc_installed_power),
            common.comparison_energy(df_ew, year, 5, 5, ptc_installed_power)
        ],
        'Jun': [
            common.comparison_energy(df_ns, year, 6, 6, ptc_installed_power),
            common.comparison_energy(df_ew, year, 6, 6, ptc_installed_power)
        ],
        'Jul': [
            common.comparison_energy(df_ns, year, 7, 7, ptc_installed_power),
            common.comparison_energy(df_ew, year, 7, 7, ptc_installed_power)
        ],
        'Aug': [
            common.comparison_energy(df_ns, year, 8, 8, ptc_installed_power),
            common.comparison_energy(df_ew, year, 8, 8, ptc_installed_power)
        ],
        'Sep': [
            common.comparison_energy(df_ns, year, 9, 9, ptc_installed_power),
            common.comparison_energy(df_ew, year, 9, 9, ptc_installed_power)
        ],
        'Oct': [
            common.comparison_energy(df_ns, year, 10, 10, ptc_installed_power),
            common.comparison_energy(df_ew, year, 10, 10, ptc_installed_power)
        ],
        'Nov': [
            common.comparison_energy(df_ns, year, 11, 11, ptc_installed_power),
            common.comparison_energy(df_ew, year, 11, 11, ptc_installed_power)
        ],
        'Dec': [
            common.comparison_energy(df_ns, year, 12, 12, ptc_installed_power),
            common.comparison_energy(df_ew, year, 12, 12, ptc_installed_power)
        ],
        'Total': [
            common.comparison_energy(df_ns, year, 1, 12, ptc_installed_power),
            common.comparison_energy(df_ew, year, 1, 12, ptc_installed_power)
        ],
        '%': [
            common.comparison_energy_percentage(df_ns, df_ew, year, 1, 12, ptc_installed_power),
            common.comparison_energy_percentage(df_ew, df_ns, year, 1, 12, ptc_installed_power)
        ]
    }
    df_comp = pd.DataFrame(data, index=['North-south', 'East-west'])
    col_comp1.dataframe(df_comp.transpose().style.apply(df_style, axis=1), height=529)

    # Comparison
    col_comp2.subheader('Earnings comparison per month')
    data = {
        'Jan': [
            common.comparison_datasets(df_ns, df, year, 1, 1),
            common.comparison_datasets(df_ew, df, year, 1, 1)
        ],
        'Feb': [
            common.comparison_datasets(df_ns, df, year, 2, 2),
            common.comparison_datasets(df_ew, df, year, 2, 2)
        ],
        'Mar': [
            common.comparison_datasets(df_ns, df, year, 3, 3),
            common.comparison_datasets(df_ew, df, year, 3, 3)
        ],
        'Apr': [
            common.comparison_datasets(df_ns, df, year, 4, 4),
            common.comparison_datasets(df_ew, df, year, 4, 4)
        ],
        'May': [
            common.comparison_datasets(df_ns, df, year, 5, 5),
            common.comparison_datasets(df_ew, df, year, 5, 5)
        ],
        'Jun': [
            common.comparison_datasets(df_ns, df, year, 6, 6),
            common.comparison_datasets(df_ew, df, year, 6, 6)
        ],
        'Jul': [
            common.comparison_datasets(df_ns, df, year, 7, 7),
            common.comparison_datasets(df_ew, df, year, 7, 7)
        ],
        'Aug': [
            common.comparison_datasets(df_ns, df, year, 8, 8),
            common.comparison_datasets(df_ew, df, year, 8, 8)
        ],
        'Sep': [
            common.comparison_datasets(df_ns, df, year, 9, 9),
            common.comparison_datasets(df_ew, df, year, 9, 9)
        ],
        'Oct': [
            common.comparison_datasets(df_ns, df, year, 10, 10),
            common.comparison_datasets(df_ew, df, year, 10, 10)
        ],
        'Nov': [
            common.comparison_datasets(df_ns, df, year, 11, 11),
            common.comparison_datasets(df_ew, df, year, 11, 11)
        ],
        'Dec': [
            common.comparison_datasets(df_ns, df, year, 12, 12),
            common.comparison_datasets(df_ew, df, year, 12, 12)
        ],
        'Total': [
            common.comparison_datasets(df_ns, df, year, 1, 12),
            common.comparison_datasets(df_ew, df, year, 1, 12)
        ],
        '%': [
            common.comparison_economic_percentage(df_ns, df_ew, df, year, 1, 12),
            common.comparison_economic_percentage(df_ew, df_ns, df, year, 1, 12)
        ]
    }
    df_comp = pd.DataFrame(data, index=['North-south', 'East-west'])
    col_comp2.dataframe(df_comp.transpose().style.apply(df_style, axis=1), height=529)


if __name__ == '__main__':
    configuration(max_width=1200)
    dashboard()
