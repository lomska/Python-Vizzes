# PACKAGES *********************************************************************************************************************

import pandas as pd
import numpy as np

import plotly.graph_objects as go

import warnings
warnings.filterwarnings('ignore')


# THE DATA *********************************************************************************************************************


df = pd.read_csv('WPP2022_DeathsBySingleAgeSex_Medium_1950-2021.csv')

# We need only the world data: year, age group, and the number of deaths:

df = df[df['Location'] == 'World'][['Time', 'AgeGrp', 'DeathTotal']]

df['DeathTotal'] = df[
    'DeathTotal'] * 1000  # deaths are given in thousands by the UN

# Uniting ages into larger age groups:

df['AgeGrp'] = df['AgeGrp'].replace('100+', '100').astype('int')


def age_group(s):
    for age in np.arange(4, 105, 5).tolist():
        if (age - 4) <= s['AgeGrp'] <= age:
            return age


df['Age_Group_5Y'] = df.apply(age_group, axis=1)  # bars coordinates


def age_group_label(s):
    for age in np.arange(4, 105, 5).tolist():
        if age < 100:
            if (age - 4) <= s['AgeGrp'] <= age:
                return str(age - 4) + '-' + str(age)
        else:
            return '100+'


df['Age_Group_Label'] = df.apply(age_group_label, axis=1)  # bars labels

# Re-group the data frame with the new 5-year groups:

dff = df.groupby(['Time', 'Age_Group_5Y',
                  'Age_Group_Label']).sum().reset_index()

dff['DeathTotal_Total'] = dff.groupby('Time')['DeathTotal'].transform(
    'sum')  # total deaths per year

dff['DeathTotal_Perc'] = dff['DeathTotal'] / dff[
    'DeathTotal_Total']  # each age group deaths as a percentage of total yearly deaths

# Besides the bars, I want to draw a dynamic line with difference for 0-4-year-olds, so two points are needed:

# moving point

dffl1 = dff[dff['Age_Group_5Y'] == 4]
dffl1['Chart'] = 'line'
dffl1['Age_Group_5Y'] = 7  # line's X1 coordinate
dffl1['Order'] = 1

# constant point

dffl2 = dffl1.copy()
dffl2['DeathTotal'] = 19780141.0  # line's Y0 coordinate: deaths in 1950
dffl2['DeathTotal_Perc'] = 0.405426  # percentage of the total as of 1950
dffl2['Order'] = 0

dffl = pd.concat(
    [dffl1, dffl2],
    ignore_index=True).sort_values(by=['Time', 'Age_Group_5Y', 'Order'])

# Adding the comparison data for 1950 to the bars:

df1950 = dff[dff['Time'] == 1950][[
    'Age_Group_5Y', 'DeathTotal', 'DeathTotal_Perc', 'DeathTotal_Total'
]].drop_duplicates().set_index('Age_Group_5Y').rename(
    columns={
        'DeathTotal': 'DeathTotal_1950',
        'DeathTotal_Perc': 'DeathTotal_Perc_1950',
        'DeathTotal_Total': 'DeathTotal_Total_1950'
    })

dff = dff.set_index('Age_Group_5Y').join(df1950).reset_index()


# THE CHART ********************************************************************************************************************


# The initial figure ***********************************************************************************************************

df_bar = dff[dff['Time'] == 1950]
df_line = dffl[dffl['Time'] == 1950]

fig = go.Figure(
    go.Bar(x=df_bar["Age_Group_5Y"],
           y=df_bar["DeathTotal"],
           width=4,
           marker_color='#404040',
           marker_line=dict(color='#010101', width=4.5),
           hoverinfo='none',
           name='1950'))  # 1950 bars

fig.add_trace(
    go.Bar(
        x=df_bar[df_bar['Age_Group_5Y'] != 4]["Age_Group_5Y"],
        y=df_bar[df_bar['Age_Group_5Y'] != 4]["DeathTotal"],
        width=4,
        marker_color='rgba(217, 217, 217, 0.4)',
        marker_line=dict(color='rgba(217, 217, 217, 1.0)', width=0.5),
        customdata=np.stack(
            (df_bar[df_bar['Age_Group_5Y'] != 4]['Time'],
             df_bar[df_bar['Age_Group_5Y'] != 4]['Age_Group_Label'],
             df_bar[df_bar['Age_Group_5Y'] != 4]['DeathTotal'] / 1000000,
             df_bar[df_bar['Age_Group_5Y'] != 4]['DeathTotal_Perc'],
             df_bar[df_bar['Age_Group_5Y'] != 4]['DeathTotal_Total'] / 1000000,
             df_bar[df_bar['Age_Group_5Y'] != 4]['DeathTotal_1950'] / 1000000,
             df_bar[df_bar['Age_Group_5Y'] != 4]['DeathTotal_Perc_1950'],
             df_bar[df_bar['Age_Group_5Y'] != 4]['DeathTotal_Total_1950'] /
             1000000),
            axis=-1),
        hovertemplate='<extra></extra><b>Age Group: %{customdata[1]} y.o.</b>\
           <br><br>%{customdata[2]:,.1f}M people died in %{customdata[0]}\
           <br>(%{customdata[3]:,.0%} of the %{customdata[4]:,.1f}M worldwide deaths)',
        name='Other Groups'))  # moving bars without the 0-4-year-olds

fig.add_trace(
    go.Bar(
        x=df_bar[df_bar['Age_Group_5Y'] == 4]["Age_Group_5Y"],
        y=df_bar[df_bar['Age_Group_5Y'] == 4]["DeathTotal"],
        width=4,
        marker_color='rgba(204, 129, 46, 0.4)',
        marker_line=dict(color='rgba(204, 129, 46, 1.0)', width=0.5),
        customdata=np.stack(
            (df_bar[df_bar['Age_Group_5Y'] == 4]['Time'],
             df_bar[df_bar['Age_Group_5Y'] == 4]['Age_Group_Label'],
             df_bar[df_bar['Age_Group_5Y'] == 4]['DeathTotal'] / 1000000,
             df_bar[df_bar['Age_Group_5Y'] == 4]['DeathTotal_Perc'],
             df_bar[df_bar['Age_Group_5Y'] == 4]['DeathTotal_Total'] / 1000000,
             df_bar[df_bar['Age_Group_5Y'] == 4]['DeathTotal_1950'] / 1000000,
             df_bar[df_bar['Age_Group_5Y'] == 4]['DeathTotal_Perc_1950'],
             df_bar[df_bar['Age_Group_5Y'] == 4]['DeathTotal_Total_1950'] /
             1000000),
            axis=-1),
        hovertemplate='<extra></extra><b>Age Group: %{customdata[1]} y.o.</b>\
           <br><br>%{customdata[2]:,.1f}M people died in %{customdata[0]}\
           <br>(%{customdata[3]:,.0%} of the %{customdata[4]:,.1f}M worldwide deaths)',
        name='5YO'))  # a moving bar for the 0-4-year-olds

fig.add_trace(
    go.Scatter(x=df_line["Age_Group_5Y"],
               y=df_line["DeathTotal"],
               mode='lines',
               line=dict(color='rgba(204, 129, 46, 1.0)', width=2,
                         dash='dash'),
               hoverinfo='none',
               name='Line'))  # a moving difference line

fig.add_trace(
    go.Scatter(
        x=[14],
        y=(df_bar[df_bar['Age_Group_5Y'] == 4]["DeathTotal"] + 19780141.0) / 2,
        mode='text',
        text=(df_bar[df_bar['Age_Group_5Y'] == 4]["DeathTotal"] - 19780141.0) /
        1000000,
        texttemplate="%{text:,.1f}M",
        textfont=dict(color='#010101', family='American Typewriter', size=18),
        textposition='middle left',
        hoverinfo='none',
        name='Line Label'))  # a moving difference line label

# Title

# The title is dynamic here, so the chart needs more traces.

fig.add_trace(
    go.Scatter(x=[45.5],
               y=[18900000],
               mode='text',
               text='CHILDREN UNDER AGE 5:',
               textfont=dict(color='rgba(204, 129, 46, 1.0)',
                             family='Californian FB',
                             size=33),
               textposition='middle right',
               name='Title-1',
               hoverinfo='none'))  # title-1

fig.add_trace(
    go.Scatter(x=[64],
               y=[15800000],
               mode='text',
               text=df_bar[df_bar['Age_Group_5Y'] == 4]["DeathTotal_Perc"],
               texttemplate="%{text:,.0%}",
               textfont=dict(color='rgba(204, 129, 46, 0.9)',
                             family='Californian FB',
                             size=71),
               textposition='middle left',
               name='Title-2',
               hoverinfo='none'))  # title-2

fig.add_trace(
    go.Scatter(x=[66],
               y=[16750000],
               mode='text',
               text="OF THE WORLD'S DEATHS",
               textfont=dict(color='rgba(217, 217, 217, 1.0)',
                             family='Californian FB',
                             size=21),
               textposition='middle right',
               name='Title-3',
               hoverinfo='none'))  # title-3

fig.add_trace(
    go.Scatter(x=[66],
               y=[15250000],
               mode='text',
               text=df_bar[df_bar['Age_Group_5Y'] == 4]["Time"],
               texttemplate="IN %{text:.0f}",
               textfont=dict(color='rgba(217, 217, 217, 1.0)',
                             family='Californian FB',
                             size=21),
               textposition='middle right',
               name='Title-4',
               hoverinfo='none'))  # title-4

# Legend

# Same story with the legend.

fig.add_trace(
    go.Scatter(x=[106],
               y=[11200000],
               mode='text',
               text=df_bar[df_bar['Age_Group_5Y'] == 4]["Time"],
               texttemplate="DEATHS DISTRIBUTION BY AGE, UN:",
               textfont=dict(color='rgba(217, 217, 217, 0.7)',
                             family='Californian FB',
                             size=18),
               textposition='middle left',
               name='Legend-Header',
               hoverinfo='none'))  # legend-header

fig.add_trace(
    go.Scatter(x=[87.5],
               y=[9800000],
               mode='markers+text',
               marker_symbol='square',
               marker_size=14,
               marker_color='rgba(217, 217, 217, 0.3)',
               marker_line=dict(color='rgba(217, 217, 217, 1.0)', width=0.3),
               text=df_bar[df_bar['Age_Group_5Y'] == 4]["Time"],
               texttemplate=" %{text:.0f}",
               textfont=dict(color='rgba(217, 217, 217, 0.7)',
                             family='Californian FB',
                             size=18),
               textposition='middle right',
               name='Legend-Marker-1',
               hoverinfo='none'))  # legend-label-1

fig.add_trace(
    go.Scatter(x=[98.5],
               y=[9800000],
               mode='markers+text',
               marker_symbol='square',
               marker_size=14,
               marker_color='#404040',
               marker_line=dict(color='#010101', width=4.5),
               text=df_bar[df_bar['Age_Group_5Y'] == 4]["Time"],
               texttemplate=" %{text:.0f}",
               textfont=dict(color='rgba(217, 217, 217, 0.7)',
                             family='Californian FB',
                             size=18),
               textposition='middle right',
               name='Legend-Marker-2',
               hoverinfo='none'))  # legend-label-2

# Animation frames *************************************************************************************************************

# For each year of comparison, an animation frame is needed:

years = dff['Time'].unique().tolist()
n_frames = len(years)

frames = []

for i in range(n_frames):

    year = years[i]
    dataframe = dff[dff['Time'] == year]
    dataframe_l = dffl[dffl['Time'] == year]
    data_for_frame = []

    data_for_frame.append(go.Bar())  # 1950 bars

    data_for_frame.append(
        go.Bar(
            x=dataframe[dataframe['Age_Group_5Y'] != 4]['Age_Group_5Y'],
            y=dataframe[dataframe['Age_Group_5Y'] != 4]["DeathTotal"],
            customdata=np.stack(
                (dataframe[dataframe['Age_Group_5Y'] != 4]['Time'],
                 dataframe[dataframe['Age_Group_5Y'] != 4]['Age_Group_Label'],
                 dataframe[dataframe['Age_Group_5Y'] != 4]['DeathTotal'] /
                 1000000,
                 dataframe[dataframe['Age_Group_5Y'] != 4]['DeathTotal_Perc'],
                 dataframe[dataframe['Age_Group_5Y'] != 4]['DeathTotal_Total']
                 / 1000000,
                 dataframe[dataframe['Age_Group_5Y'] != 4]['DeathTotal_1950'] /
                 1000000, dataframe[
                     dataframe['Age_Group_5Y'] != 4]['DeathTotal_Perc_1950'],
                 dataframe[dataframe['Age_Group_5Y'] != 4]
                 ['DeathTotal_Total_1950'] / 1000000),
                axis=-1),
            hovertemplate=
            '<extra></extra><b>Age Group: %{customdata[1]} y.o.</b>\
               <br><br>%{customdata[2]:,.1f}M people died in %{customdata[0]}\
               <br>(%{customdata[3]:,.0%} of the %{customdata[4]:,.1f}M worldwide deaths)\
               <br><br>%{customdata[5]:,.1f}M people died in 1950\
               <br>(%{customdata[6]:,.0%} of the %{customdata[7]:,.1f}M worldwide deaths)'
        ))  # moving bars without the 0-4-year-olds

    data_for_frame.append(
        go.Bar(
            x=dataframe[dataframe['Age_Group_5Y'] == 4]['Age_Group_5Y'],
            y=dataframe[dataframe['Age_Group_5Y'] == 4]["DeathTotal"],
            customdata=np.stack(
                (dataframe[dataframe['Age_Group_5Y'] == 4]['Time'],
                 dataframe[dataframe['Age_Group_5Y'] == 4]['Age_Group_Label'],
                 dataframe[dataframe['Age_Group_5Y'] == 4]['DeathTotal'] /
                 1000000,
                 dataframe[dataframe['Age_Group_5Y'] == 4]['DeathTotal_Perc'],
                 dataframe[dataframe['Age_Group_5Y'] == 4]['DeathTotal_Total']
                 / 1000000,
                 dataframe[dataframe['Age_Group_5Y'] == 4]['DeathTotal_1950'] /
                 1000000, dataframe[dataframe['Age_Group_5Y'] ==
                                    4]['DeathTotal_Perc_1950'],
                 dataframe[dataframe['Age_Group_5Y'] ==
                           4]['DeathTotal_Total_1950'] / 1000000),
                axis=-1),
            hovertemplate=
            '<extra></extra><b>Age Group: %{customdata[1]} y.o.</b>\
               <br><br>%{customdata[2]:,.1f}M people died in %{customdata[0]}\
               <br>(%{customdata[3]:,.0%} of the %{customdata[4]:,.1f}M worldwide deaths)\
               <br><br>%{customdata[5]:,.1f}M people died in 1950\
               <br>(%{customdata[6]:,.0%} of the %{customdata[7]:,.1f}M worldwide deaths)'
        ))  # a moving bar for the 0-4-year-olds

    data_for_frame.append(
        go.Scatter(
            y=dataframe_l["DeathTotal"],
            line=dict(
                color='rgba(204, 129, 46, 0.7)')))  # a moving difference line

    data_for_frame.append(
        go.Scatter(
            y=(dataframe["DeathTotal"] + 19780141.0) / 2,
            text=(dataframe[dataframe['Age_Group_5Y'] == 4]["DeathTotal"] -
                  19780141.0) / 1000000,
            textfont=dict(color='rgba(204, 129, 46, 0.7)',
                          family='Bodoni MT Condensed',
                          size=22)))  # a moving difference line label

    data_for_frame.append(go.Scatter())  # title-1

    data_for_frame.append(
        go.Scatter(text=dataframe[dataframe['Age_Group_5Y'] == 4]
                   ["DeathTotal_Perc"]))  # title-2

    data_for_frame.append(go.Scatter())  # title-3

    data_for_frame.append(
        go.Scatter(
            text=dataframe[dataframe['Age_Group_5Y'] == 4]["Time"]))  # title-4

    data_for_frame.append(go.Scatter())  # legend-header

    data_for_frame.append(
        go.Scatter(text=dataframe[dataframe['Age_Group_5Y'] == 4]
                   ["Time"]))  # legend-label-1

    data_for_frame.append(go.Scatter())  # legend-label-2

    frames.append(
        go.Frame(data=data_for_frame,
                 traces=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                 name=f"fr{i}"))

fig.update(frames=frames)

# Slider and buttons ***********************************************************************************************************

steps = []

for i in range(n_frames):
    year = years[i]
    step = dict(label=year,
                method='animate',
                args=[[f"fr{i}"],
                      dict(mode='immediate',
                           frame=dict(duration=1000, redraw=False),
                           transition=dict(duration=500))])
    steps.append(step)

sliders = [
    dict(transition=dict(duration=250),
         x=0.164,
         y=-0.13,
         len=0.811,
         currentvalue=dict(visible=False),
         steps=steps,
         active=0,
         bgcolor='rgba(217, 217, 217, 1.0)',
         bordercolor='#010101',
         borderwidth=4,
         activebgcolor='rgba(204, 129, 46, 1.0)',
         font=dict(color='#010101', family='Bodoni MT Condensed', size=1),
         ticklen=3,
         minorticklen=3,
         tickcolor='#010101')
]

play_buttons = [{
    'type':
    'buttons',
    'showactive':
    False,
    'bgcolor':
    'rgba(217, 217, 217, 0.3)',
    'bordercolor':
    'rgba(217, 217, 217, 1.0)',
    'font': {
        'color': 'rgba(217, 217, 217, 1.0)',
        'family': 'Bodoni MT Condensed',
        'size': 15
    },
    "direction":
    "left",
    'x':
    0.11,
    'y':
    -0.17,
    'buttons': [{
        'label':
        '▶',
        'method':
        'animate',
        'args': [
            None, {
                'frame': {
                    'duration': 250,
                    'redraw': False
                },
                'transition': {
                    'duration': 250
                },
                'fromcurrent': True,
                'mode': 'immediate',
            }
        ]
    }, {
        'label':
        '◼',
        'method':
        'animate',
        'args': [[None], {
            'frame': {
                'duration': 0,
                'redraw': False
            },
            'transition': {
                'duration': 0
            },
            'mode': 'immediate',
        }]
    }]
}]

# Layout ***********************************************************************************************************************

fig.update_layout(sliders=sliders,
                  updatemenus=play_buttons,
                  margin={
                      'l': 93,
                      'r': 63,
                      't': 11,
                      'b': 164,
                      'pad': 5.5
                  },
                  barmode='overlay',
                  width=850,
                  height=630,
                  bargap=0.2,
                  plot_bgcolor='#010101',
                  paper_bgcolor='#010101',
                  showlegend=False,
                  hoverlabel={'font': {
                      'size': 17,
                      'family': 'Californian FB'
                  }},
                  xaxis={
                      'range': [1, 110],
                      'title':
                      None,
                      'showgrid':
                      False,
                      'zeroline':
                      False,
                      'tickvals': [
                          2.5, 7.5, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58, 63,
                          68, 73, 78, 83, 88, 93, 98, 103.5
                      ],
                      'ticktext': [
                          0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65,
                          70, 75, 80, 85, 90, 95, 100
                      ],
                      'tickfont': {
                          'color': 'rgba(217, 217, 217, 0.6)',
                          'family': 'Bodoni MT Condensed',
                          'size': 15
                      }
                  },
                  yaxis={
                      'range': [-5, 23000000.0],
                      'title': None,
                      'showgrid': False,
                      'zeroline': False,
                      'tickvals': [5000000, 10000000, 15000000],
                      'ticktext': ['5M', '10M', '15M'],
                      'tickfont': {
                          'color': 'rgba(217, 217, 217, 0.6)',
                          'family': 'Bodoni MT Condensed',
                          'size': 15
                      }
                  })

# Annotations ******************************************************************************************************************

# This part has to be done because of Plotly's properties, just for the sake of beauty. The slider ticks don't divide values
# by 5 or 10 automatically (by 3 for some reason), so I'll do it manually.

t = 1950
x = 20.25
for n in range(16):
    fig.add_annotation(x=x,
                       y=-0.28,
                       yref='paper',
                       text=t,
                       showarrow=False,
                       font=dict(color='rgba(217, 217, 217, 5.0)',
                                 family='Bodoni MT Condensed',
                                 size=15),
                       align='center')  # labels
    t += 5
    x += 6.01

t = '|'
x = 20.5
for n in range(16):
    fig.add_annotation(x=x,
                       y=-0.23,
                       yref='paper',
                       text=t,
                       showarrow=False,
                       font=dict(color='rgba(217, 217, 217, 1.0)',
                                 family='Bodoni MT Condensed',
                                 size=4),
                       align='center')  # 'ticks'
    x += 6.01

# Axis names I'll also make manually just for designing purposes:

fig.add_annotation(xref="paper",
                   yref="paper",
                   showarrow=False,
                   text="Age:",
                   x=-0.05,
                   y=-0.063,
                   font=dict(color='rgba(217, 217, 217, 0.6)',
                             family='Bodoni MT Condensed',
                             size=18))  # X-axes-1

fig.add_annotation(xref="paper",
                   yref="paper",
                   showarrow=False,
                   text="y. o.",
                   x=1.015,
                   y=-0.063,
                   font=dict(color='rgba(217, 217, 217, 0.6)',
                             family='Bodoni MT Condensed',
                             size=18))  # X-axes-2

fig.add_annotation(xref="paper",
                   yref="paper",
                   showarrow=False,
                   text="Deaths",
                   x=-0.065,
                   y=0.93,
                   font=dict(color='rgba(217, 217, 217, 0.6)',
                             family='Bodoni MT Condensed',
                             size=18))  # Y-axes

fig.show()