"""
Utils.
"""
from typing import Dict
import math
import numpy as np


def update_rotation_angles(data: Dict, previous_data: Dict) -> None:
    """
    Update rotation angles for flight data.
    """
    for flight_data in data:
        identifier = flight_data["id"]
        if identifier not in [data["id"] for data in previous_data]:
            bearing = 0
        else:
            previous_flight_data = next(item for item in previous_data if item["id"] == identifier)
            longitude = flight_data["longitude"]
            latitude = flight_data["latitude"]
            previous_longitude = previous_flight_data["longitude"]
            previous_latitude = previous_flight_data["latitude"]
            bearing = bearing_from_positions(
                longitude,
                latitude,
                previous_longitude,
                previous_latitude,
            )

        flight_data.update(rotation_angle=bearing)
    return


def bearing_from_positions(
    longitude: float,
    latitude: float,
    previous_longitude: float,
    previous_latitude: float,
) -> float:
    """
    Compute bearing from two sets of coordinates, at
    t-1 and t. Bearing is measured clockwise from the north.

    Args:
        longitude (float): Longitude.
        latitude (float): Latitude.
        previous_longitude (float): Previous longitude.
        previous_latitude (float): Previous latitude.

    Returns:
        float: Bearing in degrees.
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [previous_latitude, previous_longitude, latitude, longitude]
    )
    # Compute the difference between the two longitudes
    dlon = lon2 - lon1
    # Compute the initial bearing
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing_rad = math.atan2(y, x)
    # Convert the bearing to degrees
    bearing_deg = math.degrees(bearing_rad)
    # Ensure the bearing is between 0 and 360 degrees
    bearing_deg = (bearing_deg + 360) % 360
    return bearing_deg


def get_closest_round_angle(angle: float) -> int:
    """
    Get closest round angle (multiple of 15 degrees)
    to the given angle.

    Args:
        angle (float): Given angle.

    Returns:
        int: Closest round angle.
    """
    round_angles = [
        0, 15, 30, 45, 60, 75, 90,
        105, 120, 135, 150, 165, 180,
        195, 210, 225, 240, 255, 270,
        285, 300, 315, 330, 345, 360,
    ]
    differences = np.array([
        angle - round_angle for round_angle in round_angles
    ])
    abs_differences = np.abs(differences)
    closest_angle_idx = abs_differences.argmin()
    closest_angle = round_angles[closest_angle_idx]
    if closest_angle == 360:
        return 0
    else:
        return closest_angle


def get_custom_icon(round_angle: int) -> Dict:
    """
    Get custom plane icon corresponding to the
    given round_angle.

    Args:
        round_angle (int): Round angle.

    Returns:
        Dict: Icon dict.
    """
    icon_url = f'https://github.com/tomseimandi/flightradar/blob/main/img/plane_{round_angle}.png?raw=true'
    return dict(
        iconUrl=icon_url,
        iconSize=[38, 38],
    )
