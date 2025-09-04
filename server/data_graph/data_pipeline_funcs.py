import geopandas as gpd
import os
import numpy as np
from shapely.geometry import Point
from shapely import force_2d
from geopandas import GeoDataFrame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) )

def read_and_convert_geojson_file(file):
    geojson_path = os.path.join(BASE_DIR, file)
    return gpd.read_file(geojson_path).to_crs("EPSG:27700")

def get_local_authority(coords, buffer):
    point = Point(coords[1], coords[0])
    coords_point = GeoDataFrame(geometry=[point], crs='EPSG:4326').to_crs('EPSG:27700')
    coords_buffered = GeoDataFrame(
    geometry=coords_point.buffer(float(buffer)),
    crs=coords_point.crs
) 
    geojson_path = os.path.join(BASE_DIR, 'data', 'geojson', 'uk-local-authorities.geojson')
    local_authority_map = gpd.read_file(geojson_path)
    local_authority_map = local_authority_map.drop_duplicates(subset=['name'])
    authority = find_features(local_authority_map, coords_buffered)
    if len(authority) > 1:
        authority_sorted = sort_by_nearest(authority, coords_point)
        authority_result = authority_sorted[["name", "distance_m"]].to_dict(orient='records')

        return authority_result
    elif len(authority) == 1:
        return [{'name': authority['name'].tolist()[0], 'distance_m': 0}]
    else:
        authority = find_nearest(local_authority_map, coords_point)
        return authority[['name', 'distance_m']].to_dict(orient="records")

def find_features(feature_gdf, point_gdf) -> GeoDataFrame:
    """Find features underneath a point with buffer

    Args:
        feature_gdf (GeoDataFrame): Feature layer
        point_gdf (GeoDataFrame): GDF of user-selected point, with buffer applied

    Returns:
        GeoDataFrame: Features underneath point and buffer
    """
    # finds features of interest underneath point selected by user
    return gpd.sjoin(feature_gdf, point_gdf, how='inner', predicate='intersects')

def sort_by_nearest(feature_gdf, point_gdf) -> GeoDataFrame:
    """When multiple features are returned, finds the distance from each feature to the selected point

    Args:
        feature_gdf (GeoDataFrame): Features close to point with buffer
        point_gdf (GeoDataFrame): GDF of selected point by user (unbuffered)

    Returns:
        GeoDataFrame: GDF of features, ordered by proximity to point
    """
    feature_gdf["distance_m"] = feature_gdf.geometry.distance(point_gdf.geometry.iloc[0])
    return feature_gdf.sort_values(by="distance_m")

def find_nearest(feature_gdf, point_gdf) -> GeoDataFrame:
    """If no features intersecting with the point, then find the nearest feature instead

    Args:
        feature_gdf (GeoDataFrame): features of interest
        point_gdf (GeoDataFrame): user-selected point

    Returns:
        GeoDataFrame: GDF of nearest feature, with distance applied
    """
    return gpd.sjoin_nearest(point_gdf, feature_gdf, how='inner', distance_col='distance_m')
       

def find_and_sort_features(feature_gdf, buffered_gdf, point_gdf) -> GeoDataFrame:
    """Find features near user-selected point, then sort by proximity

    Args:
        feature_gdf (GeoDataFrame): Features of interest
        buffered_gdf (GeoDataFrame): User-selected point - buffer
        point_gdf (GeoDataFrame): User-selected point - no buffer

    Returns:
        GeoDataFrame: Relevant features, ranked by proximity
    """
    features = find_features(feature_gdf, buffered_gdf)
    if len(features) > 0:
        features_sorted = sort_by_nearest(features, point_gdf)
    elif len(features) == 0:
        return find_nearest(feature_gdf, point_gdf)
    return features_sorted

def find_average_depth(geometry):
    """Extract average height from MultiPolygon"""
    if geometry.is_empty:
        return None
    
    if isinstance(geometry, Point):
        if geometry.has_z:
            return geometry.z
        else:
            return None
        
    z_values = []
    for polygon in geometry.geoms:
        for x, y, z in polygon.exterior.coords:
                z_values.append(z)
    
    if z_values:
        return sum(z_values) / len(z_values)
    else:
        return None

def find_geometry_area(geometry):
    """Estimate square metre val for given geometry"""
    if geometry.is_empty:
        return None  
    elif isinstance(geometry, Point):
        return 0.0
    else:
        new_geometry = force_2d(geometry)

    return new_geometry.area

def sample_features(feature_gdf, buffer_gdf, spacing):
    """Sample points inside buffered point and find features underneath each point."""
    # Generate grid of points inside buffer
    points_gdf = sampling_area(buffer_gdf, spacing)
    candidates = []
    for point in points_gdf.geometry:
        point_gdf = gpd.GeoDataFrame(geometry=[point], crs=buffer_gdf.crs)
        buffered_point_gdf = gpd.GeoDataFrame(
            geometry=point_gdf.buffer(float(50)),
            crs=point_gdf.crs
        )
        try:
            features_under_point = find_and_sort_features(feature_gdf, buffered_point_gdf, point_gdf)[['type', 'depth', 'area', 'distance_m']]
        except KeyError:
            features_under_point = find_and_sort_features(feature_gdf, buffered_point_gdf, point_gdf)
        if len(features_under_point)==1 and features_under_point.iloc[0]['distance_m'] > 50:
            features_under_point = features_under_point.iloc[1:]
        candidates.append({
            "point": point_gdf,
            "features": features_under_point
        })
    return candidates

def sampling_area(buffer_gdf, spacing):
    """Generate a grid of points spaced evenly inside buffer polygon."""
    minx, miny, maxx, maxy = buffer_gdf.total_bounds
    x_coords = np.arange(minx, maxx, spacing)
    y_coords = np.arange(miny, maxy, spacing)

    points = []
    for x in x_coords:
        for y in y_coords:
            p = Point(x, y)
            if buffer_gdf.contains(p).any():
                points.append(p)

    return gpd.GeoDataFrame(geometry=points, crs=buffer_gdf.crs)   

def remove_duplicate_features(df):
    """Remove duplicates in workings dfs"""
    area_tolerance = 1e3
    distance_tolerance = 1
    depth_tolerance = 1
    df = df.copy()
    df['area_rounded'] = (df['area'] / area_tolerance).round().astype(int)
    df['dist_rounded'] = (df['distance_m'] / distance_tolerance).round().astype(int)
    df['depth_rounded'] = (df['depth'] / depth_tolerance).round().astype(int)
    # Drop duplicates using the rounded columns
    return df.drop_duplicates(subset=['area_rounded', 'depth_rounded', 'dist_rounded']).drop(
        columns=['area_rounded', 'depth_rounded', 'dist_rounded']
    ) 
    
# if __name__ == '__main__':
    # # case 1: result in one local authority
    # result = get_local_authority([50.144072, -5.384586], 5000)
    # print('Result 1: ', result)
    # # case 2: result nearest to a duplicated local authority
    # result = get_local_authority([55.656203, -1.013223], 5000)
    # print('Result 2: ', result)
    # # case 3: result not in a local authority
    # result = get_local_authority([54.572678, -3.998464], 5000)
    # print('Result 3: ', result)
    # # case 4: overlapping authorities
    # result = get_local_authority([51.476670, -0.184388], 5000)
    # print('Result 4: ', result)

def convert_point_to_coords(point: GeoDataFrame):
    point_coords = point.to_crs(epsg=4326)
    lat, lng = point_coords.geometry.y.iloc[0], point_coords.geometry.x.iloc[0]
    return int(round(lat, 2)*100)/100, int(round(lng, 2)*100)/100

def sizing_from_mine_water(
    Q_watts: float,
    T_source_C: float,
    T_target_C: float = 35.0,
    lift_m: float = 100.0,
    user_deltaT_C: float | None = None,
    cp: float = 4186.0,
    rho: float = 1000.0,
    g: float = 9.81,
    pump_efficiency: float = 0.65,
) -> dict:
    """
    Determine flow and pump power to remove Q_watts of heat using mine water.

    Args:
      Q_watts: desired heat removal (W), e.g. 600000 for 600 kW.
      T_source_C: temperature of mine water (°C).
      T_target_C: data centre setpoint temperature (°C). Default 35°C.
      lift_m: vertical difference the water must be pumped (m).
      user_deltaT_C: optional temperature rise of the cooling water allowed (°C).
                     If None, uses the full possible rise = T_target - T_source (max).
      cp: specific heat (J/kg·K) — default 4186 for water.
      rho: density (kg/m³) — default 1000 for water.
      g: gravity (m/s²) — default 9.81.
      pump_efficiency: pump efficiency (0-1). Default 0.65.

    Returns:
      dict with:
        'feasible' (bool),
        'deltaT_used_C',
        'mass_flow_kg_s',
        'vol_flow_l_s',
        'pump_power_W',
        'pump_power_kW',
        'notes'
    """
    # check feasibility
    Tmax_possible = T_target_C - T_source_C
    if Tmax_possible <= 0:
        return {
            "feasible": False,
            "notes": (
                f"Source water ({T_source_C}°C) is not colder than the data centre "
                f"permitted temp ({T_target_C}°C). Cannot provide cooling by simple heat exchange."
            ),
        }

    # choose deltaT
    if user_deltaT_C is None:
        deltaT = Tmax_possible
    else:
        # cannot exceed physical max
        deltaT = min(user_deltaT_C, Tmax_possible)
        if deltaT <= 0:
            return {
                "feasible": False,
                "notes": "Requested deltaT is not positive or not physically possible with given temperatures.",
            }

    # mass flow (kg/s) required to remove Q_watts with given deltaT:
    m_dot = Q_watts / (cp * deltaT)   # kg/s

    vol_m3_s = m_dot / rho
    vol_l_s = vol_m3_s * 1000.0

    # pump hydraulic power (W) to lift water height lift_m (gravity only)
    # Note: include pump efficiency
    pump_power_W = (rho * g * lift_m * vol_m3_s) / max(pump_efficiency, 1e-6)
    pump_power_kW = pump_power_W / 1000.0

    return {
        "feasible": True,
        "deltaT_used_C": deltaT,
        "vol_flow_l_s": vol_l_s,
        "pump_power_kW": pump_power_kW,
        "notes": (
            "Hydraulic pump power above is gravitational lift only. Add friction/head losses to get "
            "actual pump specification. Also check heat exchanger approach and allowed return temperatures."
        ),
    }
