# PACKAGES *********************************************************************************************************************

import pandas as pd
import numpy as np

import plotly.graph_objects as go

import warnings

warnings.filterwarnings('ignore')

# THE DATA *********************************************************************************************************************

df = pd.read_csv(
    'globalterrorismdb.csv', index_col=0
)  # I merged the databases for 1970-2020 and for 2021 from https://www.start.umd.edu/gtd/

# In this example, I'll build a chart for the U.S. and for Afghanistan, the first in 1970 and the first in 2020, respectively.
# On the dashboard, you can choose whether to show the second country, and you can also select countries. To do that, dash and
# bootstrap components are needed (I didn't include them here).

# Grouping the dataframe by the number of terrorist attacks in each country/year

df = df[df['iyear'] < 2021]

dff = df.groupby([
    'iyear', 'country_txt'
])['eventid'].nunique().reset_index().sort_values(by=['iyear', 'eventid'],
                                                  ascending=[True, False])

# I'll keep only the countries which had attacks after 2010:

dff['min_year'] = dff.groupby('country_txt')['iyear'].transform(
    'min')  # the first ranking year for each country
dff['max_year'] = dff.groupby('country_txt')['iyear'].transform(
    'max')  # the last ranking year for each country

min_year_dict = dff.set_index('country_txt')['min_year'].to_dict(
)  # dicts for filling nan values (further)
max_year_dict = dff.set_index('country_txt')['max_year'].to_dict()

dff = dff[dff['max_year'] >= 2011]

# Defining the rank of each country for each year (countries with the same number of attacks will get the same rank)

dff_list = []
years = np.arange(1970, 1993).tolist() + np.arange(
    1994, 2021).tolist()  # no ranks for the 1993

for year in years:
    dff_ = dff[dff['iyear'] == year]
    dff_['rank'] = dff_.groupby('eventid', sort=False).ngroup() + 1
    dff_list.append(dff_)
dff1 = pd.concat(dff_list)

# Background matrix ************************************************************************************************************

matrix_df = dff1.groupby(['rank', 'iyear']).agg('count')[[
    'country_txt'
]].rename(columns={
    'country_txt': 'n_countries'
}).reset_index()

# A matrix must have values for each rank & year, incl when there are no ranked countries -> adding zero values:

ranks = np.arange(1, 63, 1).tolist()
countries = dff1['country_txt'].unique().tolist()

dff_1 = pd.DataFrame(pd.Series(years), columns=['iyear'])
dff_2 = pd.DataFrame(pd.Series(ranks), columns=['rank'])

dff_1['key'] = 0
dff_2['key'] = 0

dff_index = dff_1.merge(dff_2, on='key', how='outer')
dff_index = dff_index.drop('key', axis=1)

matrix_df = dff_index.set_index(['iyear', 'rank']).join(
    matrix_df.set_index(['iyear', 'rank'])).reset_index()

matrix_df['n_countries'] = matrix_df['n_countries'].fillna(0)

# Color for the matrix markers. Besides the filled and zero markers, there are also "invisible" ones in the bottom, to fix the
# chart from twitching while using dropdowns.


def color(s):
    if s['n_countries'] > 0:
        return 1
    elif s['rank'] < 61:
        return 2
    else:
        return 0


matrix_df['color'] = matrix_df.apply(color, axis=1)

# Separating each ten points (for better looks):


def index(s):
    if s['rank'] <= 10:
        return s['rank']
    elif s['rank'] <= 20:
        return s['rank'] + 1
    elif s['rank'] <= 30:
        return s['rank'] + 2
    elif s['rank'] <= 40:
        return s['rank'] + 3
    elif s['rank'] <= 50:
        return s['rank'] + 4
    else:
        return s['rank'] + 5


matrix_df['index'] = matrix_df.apply(index, axis=1)

# Lines ************************************************************************************************************************

# Each country must have values for each year (the line must "fall" to the bottom when the country is not ranked, not stay
# in the ranking area) -> adding zero values:

dff_1 = pd.DataFrame(pd.Series(years), columns=['iyear'])
dff_2 = pd.DataFrame(pd.Series(countries), columns=['country_txt'])

dff_1['key'] = 0
dff_2['key'] = 0

dff_index = dff_1.merge(dff_2, on='key', how='outer')
dff_index = dff_index.drop('key', axis=1)

dff1 = dff_index.set_index(['iyear', 'country_txt'
                            ]).join(dff1.set_index(['iyear', 'country_txt'
                                                    ])).reset_index()

dff1['eventid'] = dff1['eventid'].fillna(0)

# Filling the missing values in the added rows with earlier created year dictionaries:

dff1['min_year'] = dff1['country_txt'].map(min_year_dict)
dff1['max_year'] = dff1['country_txt'].map(max_year_dict)


# If there were no attacks during the year, and so the country had no rank,
# the line will "fall" to 62, which will be 'out' of the rating on the picture:
def rank_line(s):
    if (s['eventid'] == 0 or s['rank'] > 57) and s['iyear'] != 1993 and s[
            'iyear'] >= s['min_year'] and s['iyear'] <= s['max_year']:
        return 62
    elif (s['eventid'] == 0 or s['rank'] > 57) and s['iyear'] == 1993:
        return np.nan
    else:
        return s['rank']


dff1['rank_line'] = dff1.apply(rank_line, axis=1)


# Separating each 10 ranks in the grid
def index_line(s):
    if s['rank_line'] <= 10:
        return s['rank_line']
    elif s['rank_line'] <= 20:
        return s['rank_line'] + 1
    elif s['rank_line'] <= 30:
        return s['rank_line'] + 2
    elif s['rank_line'] <= 40:
        return s['rank_line'] + 3
    elif s['rank_line'] <= 50:
        return s['rank_line'] + 4
    else:
        return s['rank_line'] + 5


dff1['index_line'] = dff1.apply(index_line, axis=1)

# Custom data for the hoverlabels (1 will be '1st', etc.):

dff1['rank'] = dff1['rank'].fillna(0).astype('int').astype('str').replace(
    '0', '')


def rank_txt(s):
    if s['rank'] == '1' or s['rank'] == '21' or s['rank'] == '31' or s[
            'rank'] == '41' or s['rank'] == '51':
        return 'st'
    elif s['rank'] == '2' or s['rank'] == '22' or s['rank'] == '32' or s[
            'rank'] == '42' or s['rank'] == '52':
        return 'nd'
    elif s['rank'] == '3' or s['rank'] == '23' or s['rank'] == '33' or s[
            'rank'] == '43' or s['rank'] == '53':
        return 'rd'
    elif s['rank'] == '':
        return ''
    else:
        return 'th'


dff1['rank_txt'] = dff1.apply(rank_txt, axis=1)


def rank_label(s):
    return s['rank'] + s['rank_txt']


dff1['rank_label'] = dff1.apply(rank_label, axis=1)


def attacks_label(s):
    return str('{:,}'.format(int(s['eventid']))) + ' attacks'


dff1['attacks_label'] = dff1.apply(attacks_label, axis=1)


def table_label_len(s):
    return len(str(s['iyear'])) + len(s['rank_label']) + len(
        s['attacks_label'])


dff1['table_label_len'] = dff1.apply(table_label_len, axis=1)


def fill_table(s):
    return '.' * (44 - s['table_label_len'])


dff1['fill_table'] = dff1.apply(fill_table, axis=1)
dff1['table_label'] = dff1['iyear'].astype('str') + dff1['fill_table'] + dff1[
    'rank_label'] + ' (' + dff1['attacks_label'] + ')'

# Shorten the country names length to show them correctly on the sides of the chart:

dff1['country_label'] = dff1['country_txt'].replace('Bosnia-Herzegovina',
                                                    'Bosnia-<br>Herzegovina')

old_countries = [
    'Central African Republic', 'United Kingdom',
    'Democratic Republic of the Congo', 'Dominican Republic',
    'Papua New Guinea', 'Slovak Republic', 'Republic of the Congo',
    'Trinidad and Tobago', 'United Arab Emirates', 'West Bank and Gaza Strip'
]
new_countries = [
    'Central<br>African<br>Republic', 'United<br>Kingdom',
    'Democratic<br>Republic<br>of the Congo', 'Dominican<br>Republic',
    'Papua<br>New Guinea', 'Slovak<br>Republic', 'Republic<br>of the Congo',
    'Trinidad and<br>Tobago', 'United Arab<br>Emirates',
    'West Bank and<br>Gaza Strip'
]

for i in range(10):
    dff1['country_label'] = dff1['country_label'].replace(
        old_countries[i], new_countries[i])


# THE CHART ********************************************************************************************************************

    
dff211 = dff1[dff1['country_txt'] == 'United States']
dff212 = dff1[dff1['country_txt'] == 'Afghanistan']

fig = go.Figure()

fig.add_trace(
    go.Scatter(x=matrix_df['iyear'],
               y=matrix_df['index'],
               mode='markers',
               marker_color=matrix_df['color'],
               marker_colorscale=['#010101', '#777777', '#333333'],
               marker_size=3,
               name='matrix',
               hoverinfo='none'))

fig.add_trace(
    go.Scatter(
        x=dff211['iyear'],
        y=dff211['index_line'],
        mode='markers+lines',
        line_shape='hvh',
        line_width=2,
        line_color='#d9d9d9',
        marker_size=1,
        marker_color='rgba(255, 255, 255, 0)',
        name='United States',
        customdata=np.stack(
            (dff211['iyear'], dff211['rank_label'], dff211['attacks_label']),
            axis=-1),
        hovertemplate='<extra></extra><b>%{customdata[0]}</b>\
               <br>%{customdata[1]}: %{customdata[2]}'))

fig.add_trace(
    go.Scatter(
        x=[1969],
        y=dff211[dff211['iyear'] == dff211['min_year']]['index_line'],
        mode='text',
        text=dff211[dff211['iyear'] == dff211['min_year']]['country_label'],
        textfont=dict(color='#d9d9d9', family='Bodoni MT Condensed', size=20),
        textposition='middle left',
        name='United States',
        hoverinfo='none'))

fig.add_trace(
    go.Scatter(
        x=dff211[(dff211['iyear'] == dff211['min_year']) |
                 (dff211['iyear'] == dff211['max_year'])]['iyear'],
        y=dff211[(dff211['iyear'] == dff211['min_year']) |
                 (dff211['iyear'] == dff211['max_year'])]['index_line'],
        mode='markers',
        marker_size=7,
        marker_color='#d9d9d9',
        customdata=np.stack(
            (dff211[(dff211['iyear'] == dff211['min_year']) |
                    (dff211['iyear'] == dff211['max_year'])]['iyear'],
             dff211[(dff211['iyear'] == dff211['min_year']) |
                    (dff211['iyear'] == dff211['max_year'])]['rank_label'],
             dff211[(dff211['iyear'] == dff211['min_year']) |
                    (dff211['iyear'] == dff211['max_year'])]['attacks_label']),
            axis=-1),
        hovertemplate='<extra></extra><b>%{customdata[0]}</b>\
        <br>%{customdata[1]}: %{customdata[2]}',
        name='United States'))

fig.add_trace(
    go.Scatter(
        x=dff212['iyear'],
        y=dff212['index_line'],
        mode='markers+lines',
        line_shape='hvh',
        line_width=2,
        line_color='#cc812e',
        marker_size=1,
        marker_color='rgba(204, 129, 46, 0)',
        customdata=np.stack(
            (dff212['iyear'], dff212['rank_label'], dff212['attacks_label']),
            axis=-1),
        hovertemplate='<extra></extra><b>%{customdata[0]}</b>\
               <br>%{customdata[1]}: %{customdata[2]}',
        name='Afghanistan'))

fig.add_trace(
    go.Scatter(
        x=[2021],
        y=dff212[dff212['iyear'] == dff212['max_year']]['index_line'],
        mode='text',
        text=dff212[dff212['iyear'] == dff212['max_year']]['country_label'],
        textfont=dict(color='#cc812e', family='Bodoni MT Condensed', size=20),
        textposition='middle right',
        name='Afghanistan',
        hoverinfo='none'))

fig.add_trace(
    go.Scatter(
        x=dff212[(dff212['iyear'] == dff212['min_year']) |
                 (dff212['iyear'] == dff212['max_year'])]['iyear'],
        y=dff212[(dff212['iyear'] == dff212['min_year']) |
                 (dff212['iyear'] == dff212['max_year'])]['index_line'],
        mode='markers',
        marker_size=7,
        marker_color='#cc812e',
        customdata=np.stack(
            (dff212[(dff212['iyear'] == dff212['min_year']) |
                    (dff212['iyear'] == dff212['max_year'])]['iyear'],
             dff212[(dff212['iyear'] == dff212['min_year']) |
                    (dff212['iyear'] == dff212['max_year'])]['rank_label'],
             dff212[(dff212['iyear'] == dff212['min_year']) |
                    (dff212['iyear'] == dff212['max_year'])]['attacks_label']),
            axis=-1),
        hovertemplate='<extra></extra><b>%{customdata[0]}</b>\
        <br>%{customdata[1]}: %{customdata[2]}',
        name='Afghanistan'))

fig.update_layout(
    margin={
        't': 60,
        'r': 20,
        'l': 20,
        'b': 40
    },
    height=700,
    width=800,
    hoverlabel=dict(font=dict(size=30, family="Bodoni MT Condensed")),
    showlegend=False,
    plot_bgcolor='#010101',
    paper_bgcolor='#010101',
    legend=dict(itemclick='toggleothers'))

fig.update_xaxes(title=None,
                  range=[1959, 2031],
                  tickvals=[1970, 1980, 1990, 2000, 2010, 2020],
                  showticklabels=True,
                  tickfont=dict(color='#a6a6a6',
                                family='Bodoni MT Condensed',
                                size=12),
                  showgrid=False,
                  zeroline=False)

fig.update_yaxes(title=None,
                  range=[1, 63],
                  showticklabels=False,
                  showgrid=False,
                  zeroline=False,
                  autorange="reversed")

tickvals = [1, 12, 23, 34, 45, 56]
ticktext = [1, 11, 21, 31, 41, 51]

for i in range(6):
    fig.add_annotation(x=1968,
                        y=tickvals[i],
                        yref='y',
                        text=ticktext[i],
                        showarrow=False,
                        font=dict(color='rgba(217, 217, 217, 0.5)',
                                  family='Bodoni MT Condensed',
                                  size=12),
                        align='left')

fig.add_annotation(x=1966,
                    y=67,
                    yref='y',
                    text='No Rank',
                    showarrow=False,
                    font=dict(color='rgba(217, 217, 217, 0.5)',
                              family='Bodoni MT Condensed',
                              size=15),
                    align='left')

fig.add_annotation(
    x=0.625,
    y=0.95,
    ax=0.625,
    ay=1.007,
    xref='x domain',
    yref='y domain',
    axref='x domain',
    ayref='y domain',
    text='Light Positions Have Countries Ranked;<br>Dark Positions Are Empty',
    showarrow=True,
    arrowhead=3,
    arrowcolor='rgba(217, 217, 217, 0.5)',
    font=dict(color='rgba(217, 217, 217, 0.5)',
              family='Bodoni MT Condensed',
              size=15),
    align='center')

fig.show()