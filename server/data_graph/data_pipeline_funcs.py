import geopandas as gpd
from shapely.geometry import Point, Polygon

def get_local_authority(coords, buffer):
    # TODO feed in buffer
    point = Point(coords[1], coords[0])
    coords_point = gpd.GeoDataFrame(geometry=[point], crs='EPSG:4326').to_crs('EPSG:27700')
    coords_buffered = gpd.GeoDataFrame(
    geometry=coords_point.buffer(buffer),
    crs=coords_point.crs
)
    # TODO serve data from github
    local_authority_map = gpd.read_file('data/geojson/uk-local-authorities.geojson')
    local_authority_map = local_authority_map.drop_duplicates(subset=['name'])
    authority = gpd.sjoin(local_authority_map, coords_buffered, how='inner', predicate='intersects')
    if len(authority) > 1:
        authority["distance_m"] = authority.geometry.distance(coords_point.geometry.iloc[0])
        authority_sorted = authority.sort_values(by="distance_m")
        authority_result = authority_sorted[["name", "distance_m"]].to_dict(orient='records')

        return authority_result
    elif len(authority) == 1:
        return [{'name': authority['name'].tolist()[0], 'distance_m': 0}]
    else:
        authority = gpd.sjoin_nearest(coords_buffered, local_authority_map, how='inner', distance_col='distance_m')
        return authority[['name', 'distance_m']].to_dict(orient="records")

if __name__ == '__main__':
    # case 1: result in one local authority
    result = get_local_authority([50.144072, -5.384586], 5000)
    print('Result 1: ', result)
    # case 2: result in a duplicated local authority
    result = get_local_authority([55.656203, -1.013223], 5000)
    print('Result 2: ', result)
    # case 3: result not in a local authority
    result = get_local_authority([54.572678, -3.998464], 5000)
    print('Result 3: ', result)
    # case 4: overlapping authorities
    result = get_local_authority([51.476670, -0.184388], 5000)
    print('Result 4: ', result)