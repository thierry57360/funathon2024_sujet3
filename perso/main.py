import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from dash.dependencies import Output, Input, State
from FlightRadar24 import FlightRadar24API
from utils import (
    update_rotation_angles,
    get_closest_round_angle,
    get_custom_icon,
    fetch_flight_data
)

# App initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/custom.css'])

# App initialization
#app = dash.Dash(__name__)
# FlightRadar24API client
fr_api = FlightRadar24API()


default_map_children = [
    dl.TileLayer()
]

# airlines list
zones = fr_api.get_airlines()
icao_list = [''] + [item['ICAO'] for item in zones] 
company_name = [item['Name'] for item in zones]

# Mapping ICAO codes to company names
#icao_to_name = {item['ICAO']: item['Name'] for item in zones}
icao_to_name = {'': 'toutes les compagnies'} | {item['ICAO']: item['Name'] for item in zones} 

app.layout = html.Div([
    dcc.Store(id="memory"),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='zone-dropdown',
                options=[{'label': zone, 'value': zone} for zone in fr_api.get_zones().keys()],
                value='europe'
            ),
        ], className='dropdown-container right-align'),
        html.Div([
            dcc.Dropdown(
                id='company-dropdown',
                options=[{'label': icao_to_name[icao_choice], 'value': icao_choice} for icao_choice in icao_list],
                value='AFR'
            ),
        ], className='dropdown-container right-align'),
    ], className='Right-align'),
    dcc.Store(id="local", storage_type="local"),
    dcc.Store(id="session", storage_type="session"),
    dl.Map(
        id='map',
        center=[56, 10],
        zoom=6,
        style={'width': '100%', 'height': '800px'},
        children=default_map_children
    ),
    dcc.Interval(
        id="interval-component",
        interval=2*1000,
        n_intervals=0
    )
])

@app.callback(
    [Output('map', 'children'), Output('memory', 'data')],
    [Input('interval-component', 'n_intervals'), Input('zone-dropdown', 'value'), Input('company-dropdown', 'value')],
    [State('memory', 'data')]
)

# mise à jour
def update_graph_live(n, zone, airline_company, before_d):
    data = fetch_flight_data(client=fr_api, airline_icao= airline_company, zone_str=zone)
    if before_d is None:
        for flight_data in data:
            flight_data.update(rotation_angle=0)
    else:
        update_rotation_angles(data, before_d)

    # Update map children by adding markers to the default tiles layer
    children = default_map_children + [
        dl.Marker(
            id=flight['id'],
            position=[flight['latitude'], flight['longitude']],
            children=[
                dl.Popup(html.Div([
                    dcc.Markdown(f'''
                        **Compagnie aérienne**: {icao_to_name[airline_company]}.

                         **numéro du vol**: {flight['number']}.

                        **Aérport d'origine**: {flight['origin_airport_iata']}.

                        **Aéroport de destination**: {flight['destination_airport_iata']}.

                        **Vitesse au sol**: {round(flight['ground_speed'] *1.852)} Km/h.

                        **Vitesse verticale**: {round(flight['vertical_speed'] * 0.3048, 2)} m/s.

                        **altitude**: {round(flight['altitude'] * 0.3048)} m.

                        **Position**: {'en vol' if flight['on_ground'] == 0 else 'au sol'}.

                    ''')
                ]))
            ],
            icon=get_custom_icon(
                get_closest_round_angle(flight['rotation_angle'])
            ),
        ) for flight in data
    ]

    return [children, data]


if __name__ == '__main__':
    app.run_server(
        debug=True, port=5000, host='0.0.0.0'
    )
