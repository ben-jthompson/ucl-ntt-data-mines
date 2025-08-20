
import geopandas as gpd
from shapely.geometry import Point
from .data_pipeline_funcs import find_and_sort_features, read_and_convert_geojson_file

class EnvironmentalFeasibility:
    def __init__(self, coords, buffer):
        self.coords = coords
        self.point = Point(coords[1], coords[0])
        self.buffer = buffer
        self.point_gdf = gpd.GeoDataFrame(geometry=[self.point], crs='EPSG:4326').to_crs('EPSG:27700')
        self.buffered_gdf = gpd.GeoDataFrame(
            geometry=self.point_gdf.buffer(float(buffer)),
            crs=self.point_gdf.crs
        )
        
    # TODO: get geological distrubances nearby - and see 'REPORTABLE' bool to check whether important for subsidence concerns
    def get_geological_disturbances(self):
        geological_disturbances_map = read_and_convert_geojson_file('data/geojson/geological-disturbances-27700.geojson')
        disturbances = find_and_sort_features(geological_disturbances_map, self.buffered_gdf, self.point_gdf)
        print(disturbances[:10], disturbances.columns)
        print(disturbances['cnjctrd'].value_counts())
        return self.process_geological_disturbances(disturbances)

    def process_geological_disturbances(self):
        output = {'topic':'Geological Disturbances', 'risk': None, 'explanation': None}
        # TODO: fill in


    def get_terrain_type(self):
        # TODO: flag urban areas - if workings not far enough below, then problematic
        pass

    def get_flood_risk(self):
        flood_risk_map = read_and_convert_geojson_file('data/geojson/Flood_Risk_Areas.json')
        flood_risk = find_and_sort_features(flood_risk_map, self.buffered_gdf, self.point_gdf)
        return self.process_flood_risk_result(flood_risk[['distance_m', 'flood_source', 'geometry']])

    def process_flood_risk_result(self, flood_risk):
        # TODO: invoke LLM to get flood history through 
        # TODO: format as background data (LLM output), and quantitative result
        output = {'topic':'Flooding', 'risk': None, 'explanation': None}
        authority = {'Rivers and Sea': 'Environment Agency', 'Surface Water': 'Lead Local Flood Authorities'}
        nearest_flood_source = flood_risk['flood_source'].iloc[0]
        nearest_flood_risk_dist = int(flood_risk['distance_m'].iloc[0])
        distance_str = f"{nearest_flood_risk_dist}m" if nearest_flood_risk_dist < 50 else f"{round((nearest_flood_risk_dist/1000), 1)}km"
        authority_explanation = authority[nearest_flood_source]
        if nearest_flood_risk_dist == 0:
            output['risk'] = 'High'
            output['explanation'] = f"Selected area designated as place of 'Significant Flood Risk', as defined by the {authority_explanation} due to exposure to flood via {nearest_flood_source.lower()}. "
        if output['risk'] != None and len(flood_risk['flood_source'].unique()) > 1:
            secondary_risk = flood_risk[flood_risk['flood_source'] != nearest_flood_source].iloc[0]
            secondary_distance = int(secondary_risk['distance_m'])
            distance_str = f"{secondary_distance}m" if secondary_distance < 50 else f"{round((secondary_distance/1000), 1)}km"
            output['explanation'] += f"There is also a secondary flood risk from {secondary_risk['flood_source'].lower()}, approximately {distance_str} from your selected point. "
        if output['risk'] == None and nearest_flood_risk_dist < self.buffer:
            output['risk'] = 'High' if nearest_flood_risk_dist < 2500 else 'Moderate'
            output['explanation'] = f'There is a high flood risk zone, as defined by the {authority_explanation}, within your selected buffer zone of {int(self.buffer/1000)}km, due to exposure from {nearest_flood_source.lower()}. However, the flood risk boundary is located {distance_str} from your selected point. '
        elif output['risk'] == None:
            output['risk'] = 'Low'
            output['explanation'] = f'Low risk: high flood risk zones, as defined by the Environment Agency and Local Lead Flood Authorities, are not contained within your zone of interest. Nearest high flood risk zone: {distance_str}. '  

        output['explanation'] += "View the flood risk layer in the results map for more information."
        return(output)


if __name__ == '__main__':
    ef = EnvironmentalFeasibility([54.96433331, -1.616667], 5000)
    ef.get_geological_disturbances()
