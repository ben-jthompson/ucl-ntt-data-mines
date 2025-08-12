import geopandas as gpd
from shapely.geometry import Point
from geopandas import GeoDataFrame

def read_and_convert_geojson_file(file):
    return gpd.read_file(file).to_crs("EPSG:27700")

def get_local_authority(coords, buffer):
    # TODO feed in buffer
    point = Point(coords[1], coords[0])
    coords_point = GeoDataFrame(geometry=[point], crs='EPSG:4326').to_crs('EPSG:27700')
    coords_buffered = GeoDataFrame(
    geometry=coords_point.buffer(buffer),
    crs=coords_point.crs
)
    # TODO serve data from github
    local_authority_map = gpd.read_file('data/geojson/uk-local-authorities.geojson')
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

if __name__ == '__main__':
    # case 1: result in one local authority
    result = get_local_authority([50.144072, -5.384586], 5000)
    print('Result 1: ', result)
    # case 2: result nearest to a duplicated local authority
    result = get_local_authority([55.656203, -1.013223], 5000)
    print('Result 2: ', result)
    # case 3: result not in a local authority
    result = get_local_authority([54.572678, -3.998464], 5000)
    print('Result 3: ', result)
    # case 4: overlapping authorities
    result = get_local_authority([51.476670, -0.184388], 5000)
    print('Result 4: ', result)