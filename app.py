import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from geopy.geocoders import Nominatim

geolocator = Nominatim()

gun_data = pd.read_csv('final_data.csv')

incident_tags = []
for s in gun_data['tags']:
    tag = []
    if (len(s[1:-1]) > 0):
        li = s[1:-1].split("', '")
        for t in li:
            if t:
                tag.append(t)
    if tag:
        tag[0] = tag[0][1:]
        tag[-1] = tag[-1][:-1]
    incident_tags.append(tag)
def get_text(gun_data, i):
    text = "Date: " + gun_data['Incident Date'][i] + "<br>"
    text += "Address: " + gun_data['Address'][i] + "<br>"
    if len(incident_tags[i]):
        if len(incident_tags[i]) > 2:
            text += "Incident Characteristics: " + str(incident_tags[i][:2])[1:-1]
        else:
            text += "Incident Characteristics: " + gun_data['tags'][i][1:-1]
    return text

from geopy.exc import GeocoderTimedOut

def do_geocode(address, attempt=1, max_attempts=5):
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        raise

def geocode_address(address):
    location = do_geocode(address)
    return location.longitude, location.latitude, 14


def get_year(year):
    for i,j in enumerate(gun_data['Incident Date']):
        if str(j)[-4:] == year:
            return i
    return 0

end_2019 = get_year('2018')
end_2018 = get_year('2017')
end_2017 = get_year('2016')
end_2016 = get_year('2015')
end_2015 = get_year('2014')

def get_index(year):
    if year == '2019':
        return 0, end_2019, 'green'
    elif year == '2018':
        return end_2019, end_2018, 'blue'
    elif year == '2017':
        return end_2018, end_2017, 'grey'
    elif year == '2016':
        return end_2017, end_2016, 'purple'
    elif year == '2015':
        return end_2016, end_2015, 'gold'
    elif year == '2014':
        return end_2015, 400, 'brown'
    else:
        return 0, 400



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiaGFpbWluZzIiLCJhIjoiY2syem91YXp3MGVwbTNtcWlncnU2bXJvZyJ9.j7YvkG1KFA43x7lTMxSrDQ"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Gun violence local map",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-88.236604, lat=40.108087),
        zoom=12,
    ),
)


app.layout = html.Div(children=[
    html.H1(children='Gun violence'),

    html.Div(children='''
        gun violence map for Champaign-Urbana area
    '''),
    dcc.Input(id='my-id', type="text", placeholder="enter your address", debounce=True),
    html.Button('Click Me', id='button'),
    dcc.Graph(
        id='updated_map',
    ),
])

@app.callback(
    Output(component_id='updated_map', component_property='figure'),
    [Input('button', 'n_clicks')],
    state=[State(component_id='my-id', component_property='value')]
)



def update_graph_1(n, input):
    if input == None:
        res = [-88.236604, 40.108087, 12]
    else:
        res = geocode_address(input)
    return {
        'data': [
        dict(
            type="scattermapbox",
            lon=[float(i.split(',')[1][3:-2]) for i in gun_data['geo'][get_index(str(k))[0]:get_index(str(k))[1]]],
            lat=[float(i.split(',')[0][2:-1]) for i in gun_data['geo'][get_index(str(k))[0]:get_index(str(k))[1]]],
            text=[get_text(gun_data, i) for i in range(get_index(str(k))[0],get_index(str(k))[1])],
            marker=dict(size=4, opacity=0.6,color=get_index(str(k))[2]),
            name = str(k),
        ) for k in range(2014,2020)
        ],
        'layout': dict(
            autosize=True,
            automargin=True,
            margin=dict(l=30, r=30, b=20, t=40),
            hovermode="closest",
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            legend=dict(font=dict(size=10), orientation="h"),
            title="Gun violence local map",
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style="light",
                center=dict(lon=res[0], lat=res[1]),
                zoom=res[2],
            )
            )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
