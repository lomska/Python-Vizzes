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

# In this chart, I map the terrorist attacks in France by year and month. On the dashboard, you can select a country.
# To do that, dash and bootstrap components are needed (I didn't include them here).

# There are only a few rows with no information about the month of attack, so we can easily leave them out:

df = df[df['imonth'] > 0]

# Mapping the months:

month_dict = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}
df['month'] = df['imonth'].map(month_dict)

# Re-ordering months for the heatmap (the first is the outer circle, the last is the inner):

month_order = {
    'January': 12,
    'February': 11,
    'March': 10,
    'April': 9,
    'May': 8,
    'June': 7,
    'July': 6,
    'August': 5,
    'September': 4,
    'October': 3,
    'November': 2,
    'December': 1
}
df['month_order'] = df['month'].map(month_order)

# Grouping the dataframe by the number of attacks in each month, year, and country:

dff = df.groupby(['country', 'country_txt', 'month_order', 'month',
                  'iyear']).agg('count')[['eventid']].reset_index()

# I'll filter out countries where the last terrorist attack took place before 2011;
# Also, only six months of the year 2021 are available at the moment, so I'll filter it out;
# Besides that, let's keep only top-50 countries by the total number of terrorist attacks during 2011-2020.

dff = dff[dff['iyear'] < 2021]
dff['last_year'] = dff.groupby('country_txt')['iyear'].transform('max')
dff = dff[dff['last_year'] > 2010]
dff['max_attacks_total'] = dff.groupby('country_txt')['eventid'].transform(
    'sum')
top_50_index = dff[[
    'country_txt', 'max_attacks_total'
]].drop_duplicates().sort_values(
    by='max_attacks_total',
    ascending=False).head(50).set_index('country_txt').drop(
        'max_attacks_total', axis=1)
dff = top_50_index.join(dff.set_index('country_txt')).reset_index()
dff = dff.drop(['last_year', 'max_attacks_total'], axis=1)

# For the heatmap, we need to have a cell for each country, year, and month -> zero values need to be added:

dff_1 = dff[['country',
             'country_txt']].drop_duplicates().reset_index(drop=True)
dff_2 = pd.DataFrame(pd.Series(np.arange(1970, 2021, 1)), columns=['iyear'])
dff_3 = dff[['month_order', 'month']].drop_duplicates().reset_index(drop=True)

dff_1['key'] = 0
dff_2['key'] = 0
dff_3['key'] = 0

dff_index_ = dff_1.merge(dff_2, on='key', how='outer')
dff_index = dff_index_.merge(dff_3, on='key', how='outer')
dff_index = dff_index.drop('key', axis=1)

dff = dff_index.set_index([
    'country', 'country_txt', 'month_order', 'month', 'iyear'
]).join(
    dff.set_index(['country', 'country_txt', 'month_order', 'month',
                   'iyear'])).reset_index()

dff['eventid'] = dff['eventid'].fillna(0)

# Making the radials ***********************************************************************************************************

# Defyning angles with each decade separated by space:

angle_dict = dict()

years = dff['iyear'].unique().tolist()

for year in years[:10]:
    angle_dict[year] = (year - 1970) * 4 + 1
for year in years[10:20]:
    angle_dict[year] = (year - 1970) * 4 + 3
for year in years[20:30]:
    angle_dict[year] = (year - 1970) * 4 + 5
for year in years[30:40]:
    angle_dict[year] = (year - 1970) * 4 + 7
for year in years[40:50]:
    angle_dict[year] = (year - 1970) * 4 + 9
for year in years[50:]:
    angle_dict[year] = (year - 1970) * 4 + 11

dff['year_index'] = dff['iyear'].map(angle_dict)

# Colors ***********************************************************************************************************************

# The number of attacks varies from zero to 503, and we still want to see small values, so it's better to use a logarithmic
# colorscale:

dff['eventid_log'] = np.log10(dff['eventid'])
dff['eventid_log'] = dff['eventid_log'].replace([np.inf, -np.inf], 0)
dff['eventid_log_perc'] = dff['eventid_log'] / dff['eventid_log'].max()

colorscale = [
    [0, 'rgba(1,1,3,0.0)'],
    [0.3333333333333333, 'rgba(255,255,255,0.5)'],  #log10 = 1 (tenths)
    [0.6666666666666666, 'rgba(248,166,80,0.7)'],  #log10 = 2 (hundreds)
    [0.9005226616853091,
     'rgba(204,54,0, 0.8)'],  # <- this is the actual monthly maximum (503)
    [0.9260504167945478, 'rgba(204,54,0, 0.3)'
     ],  # <- this step is for the colorbar to become transparent on the top
    [1, 'rgba(1,1,3,0.0)']
]  # <- ...as well as this one (log10 = 3)

# THE CHART ********************************************************************************************************************

# In this example, I'll build a circle heatmap for France. To toggle countries, dash + bootstrap components are needed.

dfff = dff[dff['country_txt'] == 'France']

fig = go.Figure()

size = 4  # marker height
base = 90  # initial radius

month_indexes = dfff['month_order'].unique().tolist()
titles = dfff['month'].unique().tolist()
colorscale = colorscale

# Circles are built one-by-one, from the inner to the outer:

for i in range(12):
    data = dfff[dfff['month_order'] == month_indexes[i]]

    fig.add_trace(
        go.Barpolar(
            r=[size] * 51,
            theta=(data['year_index']) * 1.09,
            base=[base] * 51,
            width=[2.7] * 51,
            marker_cauto=False,
            marker_color=data['eventid_log_perc'],
            marker_colorscale=colorscale,
            marker_colorbar={
                'x': 0.09,
                'y': 0.78,
                'lenmode': 'pixels',
                'len': 250,
                'outlinecolor': '#010103',
                'outlinewidth': 1,
                'separatethousands': True,
                'showticklabels': True,
                'thickness': 12,
                'ticks': 'inside',
                'ticklen': 15,
                'ticklabelstep': 1,
                'tickcolor': '#010103',
                'thicknessmode': 'pixels',
                'tickvals': [0.3333333333333333, 0.6666666666666666],
                'ticktext': ['  10', '  100'],
                'tickfont': {
                    'color': 'rgba(217, 217, 217, 0.7)',
                    'family': 'Bodoni MT Condensed',
                    'size': 12
                },
                'tickwidth': 6
            },
            marker_cmin=0.0,
            marker_cmax=1.0,
            marker_line_color='rgba(217, 217, 217, 0.7)',
            marker_line_width=0.3,
            customdata=np.stack(
                (data['iyear'], data['month'], data['eventid']), axis=-1),
            hovertemplate='<extra></extra>%{customdata[1]} %{customdata[0]}:\
            <br>%{customdata[2]:,.0f} attacks',
            name=titles[i]))  # cells

    base += (size + 3)

fig.add_trace(
    go.Scatterpolar(r=[80] * 40,
                    theta=(data['year_index']) * 1.09,
                    mode='lines',
                    line=dict(color='rgba(217, 217, 217, 0.9)',
                              width=0.6,
                              dash='dot'),
                    hoverinfo='none'))  # dashed line

fig.add_trace(
    go.Scatterpolar(r=[80],
                    theta=[180],
                    mode='markers',
                    marker=dict(size=7, symbol='arrow-left'),
                    marker_color='rgba(217, 217, 217, 0.9)',
                    hoverinfo='none'))  # dashed line arrow

# LAYOUT ***********************************************************************************************************************

fig.update_layout(
    title_font=dict(color='rgba(217, 217, 217, 0.5)',
                    family='Bodoni MT Condensed',
                    size=50),
    plot_bgcolor='#010103',
    paper_bgcolor='#010103',
    height=750,
    width=750,
    margin={
        't': 20,
        'b': 20,
        'r': 50,
        'l': 0
    },
    showlegend=False,
    xaxis=dict(range=[0, 100],
               showgrid=False,
               showticklabels=False,
               zeroline=False),
    yaxis=dict(range=[0, 100],
               showgrid=False,
               showticklabels=False,
               zeroline=False),
    hoverlabel=dict(font=dict(size=30, family="Bodoni MT Condensed")),
    polar=dict(radialaxis=dict(range=[0, 190],
                               showticklabels=True,
                               angle=90,
                               side='counterclockwise',
                               tickangle=90,
                               tickvals=[
                                   92.5, 99.5, 106.5, 113.5, 120.5, 127.5,
                                   134.5, 141.5, 148.5, 155.5, 162.5, 169.5
                               ],
                               ticktext=[
                                   'December     ', 'November     ',
                                   'October     ', 'September     ',
                                   'August     ', 'July     ', 'June     ',
                                   'May     ', 'April     ', 'March     ',
                                   'February     ', 'January     '
                               ],
                               showgrid=False,
                               showline=False,
                               tickfont=dict(color='rgba(217, 217, 217, 0.7)',
                                             family='Bodoni MT Condensed',
                                             size=15)),
               angularaxis=dict(showticklabels=True,
                                showgrid=False,
                                showline=False,
                                direction='clockwise',
                                tickvals=[1, 46, 92, 139, 184, 230],
                                ticktext=[1970, 1980, 1990, 2000, 2010, 2020],
                                tickfont=dict(color='rgba(217, 217, 217, 0.7)',
                                              family='Bodoni MT Condensed',
                                              size=15))))

fig.update_polars(bgcolor='rgba(1, 1, 1, 0)')

fig.show()