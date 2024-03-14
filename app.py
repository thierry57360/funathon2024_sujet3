from typing import Optional
import dash
from dash import dcc
from dash import html
import dash_leaflet as dl
from dash.dependencies import Output, Input
from FlightRadar24 import FlightRadar24API


fr_api = FlightRadar24API()


def fetch_flight_data(
    airline_icao: Optional[str] = None,
    aircraft_type: Optional[str] = None,
    zone_str: Optional[str] = None
):
    """
    Fetch flight data from FlightRadar24 API for
    a given airline, aircraft type and zone.

    Args:
        airline_icao (str): ICAO code of the airline.
        aircraft_type (str): Type of aircraft.
        zone_str (str): Zone string.

    Returns:
        List: Flights.
    """
    zone = fr_api.get_zones()[zone_str]
    bounds = fr_api.get_bounds(zone)

    flights = fr_api.get_flights(
        aircraft_type=aircraft_type,
        airline=airline_icao,
        bounds=bounds
    )
    return [
        {
            "latitude": flight.latitude,
            "longitude": flight.longitude,
            "id": flight.id,
        } for flight in flights
    ]


app = dash.Dash(__name__)


default_map_children = [
    dl.TileLayer()
]


app.layout = html.Div([
    dl.Map(
        id='map',
        center=[56, 10],
        zoom=6,
        style={'width': '100%', 'height': '800px'},
        children=default_map_children
    ),
    dcc.Interval(
        id="interval-component",
        interval=2*1000,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(
    Output('map', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    data = fetch_flight_data(airline_icao="AFR", zone_str="europe")

    # Assuming data is a list of dict with 'latitude', 'longitude' and 'flight' keys
    # You may need to adjust this based on your actual data structure
    children = default_map_children + [
        dl.Marker(position=[flight['latitude'], flight['longitude']], children=[
            dl.Popup(html.Div([
                html.H3(flight['id'])
            ]))
        ]) for flight in data
    ]

    return children


if __name__ == '__main__':
    app.run_server(
        debug=True, port=5000, host='0.0.0.0'
    )
