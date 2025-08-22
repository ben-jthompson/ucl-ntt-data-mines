import geopandas as gpd
from shapely.geometry import Point
from .data_pipeline_funcs import find_and_sort_features, read_and_convert_geojson_file

class CoolingFeasibility:
    def __init__(self, coords, buffer):
        self.coords = coords
        self.point = Point(coords[1], coords[0])
        self.buffer = buffer
        self.point_gdf = gpd.GeoDataFrame(geometry=[self.point], crs='EPSG:4326').to_crs('EPSG:27700')
        self.buffered_gdf = gpd.GeoDataFrame(
            geometry=self.point_gdf.buffer(float(buffer)),
            crs=self.point_gdf.crs
        )
    def get_temperature_differentials(self):
        # find the temperature for the nearest area and the different depths
        pass

    def get_mine_workings(self):
        # find mine workings depth and status
            # TODO: look at equations for cooling - heat pumps and heat exchanger (https://www.mdpi.com/1996-1073/14/19/6215)
            # TODO: look at ashrae conditions and work out formula for areal extent -> dc capacity -> cooling requirements -> temperature 
        pass

    def get_aquifer_status(self):
        aquifer_map = read_and_convert_geojson_file('data/geojson/aquifers-cropped-4326.geojson')
        # CLASS: 
        # numbers: Character
        # 1: Significant intergranular flow
        # 2: Flow is virtually all through fractures and other discontinuities
        # 3: Virtually non-existent flow
        # letters: Character
        # A: Highly productive aquifer
        # B: Moderately productive aquifer
        # C:  Low productivity aquifer
        #  : Rocks with essentially no groundwater
        
        aquifers = find_and_sort_features(aquifer_map, self.buffered_gdf, self.point_gdf)
        self.output = [self.process_aquifer_result(aquifers[['distance_m', 'SUMMARY', 'CLASS', 'geometry']])]
        
    # def process_aquifer_result(self, aquifers):
        # TODO: invoke llm for sample output, then use that for template response
        # TODO: grant score for each CLASS output
        # TODO: give idea of pumping cost - eg. for the distance from each aquifer to the point - horizontal dist
        # TODO: if there is no distance = 0 in the GDF, say there is no information for aquifers directly below the point
        # output = {'topic':'Aquifers', 'suitability': None, 'explanation': None}   
    
    def process_aquifer_result(self, aquifers):
        flow_mechanisms = {
            '1': ["significant intergranular flow", 1],
            '2': ["flow being virtually all through fractures and other discontinuities", 0.5],
            '3': ["virtually non-existent flow", 0.1]
        }
        productivities = {
            'A': ['High', 1, 'designated a principal aquifer, this is largely composed of geological formations of high permeability and water storage capacity, typically supporting public water supplies and river base flows'],
            'B': ['Medium', 0.6, 'designated a secondary aquifer, this is largely composed ofgeological formations of lower permeability than principal aquifers, but still capable of providing some water supply or supporting surface water flows'],
            'C': ['Low', 0.2, 'designated as unproductive, this is largely composed of geological formations with very low permeability, meaning they are unlikely to provide significant water supplies or support surface water and ecosystems']
        }

        output = {
            'topic': 'Aquifers',
            'suitability': None,
            'explanation': ""
        }
        aquifer_scores = []
        for index, aquifer in aquifers.iterrows():
            if len(aquifer['CLASS'])==1:
                productivity = ['None', 0, 'designated as unproductive, this is largely composed of geological formations with very low permeability, meaning they are unlikely to provide significant water supplies or support surface water and ecosystems']
            else:
                productivity = productivities[aquifer['CLASS'][1]]
            
            flow_mecha = flow_mechanisms[aquifer['CLASS'][0]]
            distance = aquifer['distance_m']
            suitability_score = round(self.calculate_aquifer_suitability(productivity[1], flow_mecha[1], distance), 2)
            rank = 1
            for i in range(len(aquifer_scores)):
                if aquifer_scores[i]['suitability'] < suitability_score:
                    aquifer_scores[i]['rank'] += 1
                else:
                    rank+=1
            aquifer_scores.append({'distance': int(distance), 'description': [productivity[0], productivity[2], flow_mecha[0]], 'suitability': suitability_score, 'rank': rank})
            
        nearest_aquifer = aquifer_scores[0]
        best_aquifer = [aquifer for aquifer in aquifer_scores if aquifer['rank'] == 1][0]
        if nearest_aquifer['distance'] == 0:
            output['explanation'] = f"The aquifer below the selected point is a {nearest_aquifer['description'][0].lower()} productivity aquifer - {nearest_aquifer['description'][1]}. "
        else:
            output['explanation'] = f"The aquifer below the selected point is a {nearest_aquifer['description'][0].lower()} productivity aquifer - {nearest_aquifer['description'][1]}. "
        if nearest_aquifer != best_aquifer:
            output['explanation'] += f"However, the most appropriate aquifer is a {best_aquifer['description'][0].lower()} productivity aquifer - {best_aquifer['description'][2]}, with {best_aquifer['description'][1]}. This aquifer is located {best_aquifer['distance']}m from the selected point."
        
        if best_aquifer['suitability'] > 0.75:
            output['explanation'] += "The optimal nearby aquifer conditions are suitable for a data centre project."
            output['suitability'] = 'High'
        elif best_aquifer['suitability'] > 0.50:
            output['explanation'] += "The optimal nearby aquifer conditions are challenging, but could be used for a data centre project."
            output['suitability'] = 'Medium'
        else:
            output['explanation'] += "The optimal nearby aquifer conditions are very challenging and most likely unsuitable for a data centre project."
            output['suitability'] = 'Low'

        return output

    def calculate_aquifer_suitability(self, productivity, flow_mecha, distance):
        # TODO: make figure of aquifer suitability?
        return (productivity + flow_mecha - distance/20000 ) / 2
    
    def add_supplementary_information(self):
        # TODO: link up
        self.output.append({'topic': 'Geothermal Information', 'explanation': """For a proposed groundwater-source, open-loop geothermal system (regardless of whether 
aquifer or mine water derived), the Environment Agency (EA) is the principal regulator for 
England. They are responsible for managing abstraction and reinjection applications and 
licences.  
It is advisable in the first instance to have a discussion with the EA about the proposed scheme. 
They can therefore make the most up-to-date recommendations on the procedures needed to 
be complied with.  
At present, a number of consents, permits and licences will be required for a full-scale scheme 
from the EA. These may include:  
Groundwater Investigation Consent (WR32) 
Abstraction licence  
Reinjection/discharge permit (via an Environmental Permit)"""})


    def run(self):
        self.get_aquifer_status()
        self.add_supplementary_information()
        return self.output

if __name__ == '__main__':
    cf = CoolingFeasibility([53.383331, -1.566667], 5000)
    cf.get_aquifer_status()