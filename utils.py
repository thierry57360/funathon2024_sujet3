"""
Utils.
"""
import math


custom_icon = dict(
    iconUrl='https://github.com/tomseimandi/flightradar/blob/main/img/plane.png?raw=true',
    iconSize=[38, 38],
)


def update_rotation_angles(data, previous_data):
    """
    Update rotation angles for flight data.
    """
    for flight_data in data:
        identifier = flight_data["id"]
        if identifier not in [data["id"] for data in previous_data]:
            rotation_angle = 0
        else:
            longitude = data["longitude"]
            latitude = data["latitude"]
            previous_longitude = previous_data["longitude"]
            previous_latitude = previous_data["latitude"]
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [previous_latitude, previous_longitude, latitude, longitude])
            # Compute the difference between the two longitudes
            dLon = lon2 - lon1
            # Compute the initial bearing
            y = math.sin(dLon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
            bearing_rad = math.atan2(y, x)
            # Convert the bearing to degrees
            bearing_deg = math.degrees(bearing_rad)
            # Ensure the bearing is between 0 and 360 degrees
            rotation_angle = (bearing_deg + 360) % 360

        flight_data.update(rotation_angle=rotation_angle)
