from flask_sqlalchemy import SQLAlchemy

# Create db here to avoid circular imports
# Both app.py and all routes will import from this file
db = SQLAlchemy()

import math
def calculate_distance(lat1, lon1, lat2, lon2):
    # Rough approximation of distance in kilometers using Haversine formula
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
