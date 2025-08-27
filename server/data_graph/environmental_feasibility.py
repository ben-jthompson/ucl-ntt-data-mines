import numpy as np
import geopandas as gpd
import datetime as dt
import os
from shapely.geometry import Point
import contextily as ctx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Transformer
from .data_pipeline_funcs import find_and_sort_features, read_and_convert_geojson_file, sample_features
from ..formatting_graph.formatter_utils import file_format_string

class EnvironmentalFeasibility:
    def __init__(self, coords, buffer, client_id):
        self.coords = coords
        self.client_id = client_id
        self.point = Point(coords[1], coords[0])
        self.buffer = buffer
        self.point_gdf = gpd.GeoDataFrame(geometry=[self.point], crs='EPSG:4326').to_crs('EPSG:27700')
        self.buffered_gdf = gpd.GeoDataFrame(
            geometry=self.point_gdf.buffer(float(buffer)),
            crs=self.point_gdf.crs
        )
        
    def get_geological_disturbances(self):
        geological_disturbances_map = read_and_convert_geojson_file('data/geojson/geological-disturbances-27700.geojson')
        disturbances = find_and_sort_features(geological_disturbances_map, self.buffered_gdf, self.point_gdf)
        disturbances.drop('index_right', axis=1, inplace=True)
        spacing = self.buffer/5
        disturbance_candidates = sample_features(disturbances, self.buffered_gdf, spacing)
        return self.process_geological_disturbances(disturbances, disturbance_candidates)

    def process_geological_disturbances(self, disturbances, disturbance_candidates):
        output = {'topic':'Geological Disturbances', 'risk': None, 'explanation': None}
        def calculate_bracket(candidate):
            if len(candidate['features']) > 5 and candidate['features'].iloc[0]['distance_m'] < 25:
                candidate['bracket'] = 'Low'
            elif len(candidate['features']) > 5 and candidate['features'].iloc[0]['distance_m'] >= 50:
                candidate['bracket'] = 'Middle'
            elif 0 < len(candidate['features']) < 2 and candidate['features'].iloc[0]['distance_m'] < 50:
                candidate['bracket'] = 'Middle'
            else:
                candidate['bracket'] = 'High'
        for candidate in disturbance_candidates:
            calculate_bracket(candidate)
            
        values = disturbances['type'].value_counts()
        conjectures = np.round((len(disturbances[disturbances['cnjctrd']=='TRUE'])/len(disturbances))*100, 2)
        distances = disturbances['distance_m'].to_list()
        min_dist = np.round(distances[0],2)#
        total_faults = len(distances)

        output['explanation'] = f"Closest disturbance to the central point is a {disturbances.iloc[0]['type'].lower()}, located {min_dist}m away."
        output['explanation'] += f"In the feature map below, red implies many disturbances (over five) within a 50m radius from the point, with the closest disturbance less than 25m from the centre. Yellow implies over five disturbances, but all over 25m away - or, fewer disturbances, but closer than 25m. Green indicates less than five disturbances, all further than 25m." 
        if conjectures > 10:
            output['explanation'] += f"It is important to know that, of the {total_faults} disturbances, {conjectures}% are not verified - therefore, they will need to be properly georeferenced."
        print(output['explanation'])
        img_path = self.render_disturbances_image(disturbance_candidates)
        output['fig'] = [f"{img_path}.png", 'Geological Disturbances Risk Map']
        return output

    def render_disturbances_image(self, disturbance_candidates):
        fig, ax = plt.subplots(figsize=(10, 10))

        points = []
        brackets = []

        for candidate in disturbance_candidates:
            point = candidate["point"].geometry.iloc[0]
            points.append(point)
            brackets.append(candidate.get("bracket", "Low"))
        plot_gdf = gpd.GeoDataFrame(
            {"bracket": brackets},
            geometry=points,
            crs=disturbance_candidates[0]["point"].crs
        )

        bracket_map = {"Low": 0, "Middle": 1, "High": 2}
        plot_gdf["bracket_num"] = plot_gdf["bracket"].map(bracket_map)

        plot_gdf = plot_gdf.to_crs(epsg=3857)
        plot_gdf_latlng = plot_gdf.to_crs(epsg=4326)
        plot_gdf["lng"] = plot_gdf_latlng.geometry.x
        plot_gdf["lat"] = plot_gdf_latlng.geometry.y

        # Plot with RdYlGn colormap
        scatter = plot_gdf.plot(
            ax=ax,
            column="bracket_num",
            marker="*",
            markersize=150,
            cmap="RdYlGn",
            legend=True, 
            vmin=0, 
            vmax=2,
            legend_kwds={'label': "Disturbance Bracket", 'shrink': 0.6} ,   
            edgecolor="black", 
            linewidth=0.8 
        )

        cbar = scatter.get_legend()
        if cbar is not None:
            ticks = [0, 1, 2]
            cbar.set_ticks(ticks)
            cbar.set_ticklabels(["Low", "Middle", "High"])

        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
        lng_min, lat_min = transformer.transform(xmin, ymin)
        lng_max, lat_max = transformer.transform(xmax, ymax)

        ax.set_xticks([xmin, xmax])
        ax.set_xticklabels([f"{lng_min:.2f}", f"{lng_max:.2f}"])

        ax.set_yticks([ymin, ymax])
        ax.set_yticklabels([f"{lat_min:.2f}", f"{lat_max:.2f}"])

        ctx.add_basemap(ax, crs='EPSG:3857', source=ctx.providers.Esri.WorldStreetMap, alpha=0.75)
        plt.tight_layout()
        now = str(dt.datetime.now())
        image_dir = os.path.join(os.getcwd(), 'server/uploads', str(self.client_id), 'report')
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, file_format_string(f'disturbance_img{now}'))
        print("IMGPATH: ", image_path)
        plt.savefig(image_path, dpi=300)
        plt.close(fig)
        return image_path

    def get_flood_risk(self):
        flood_risk_map = read_and_convert_geojson_file('data/geojson/Flood_Risk_Areas.json')
        flood_risk = find_and_sort_features(flood_risk_map, self.buffered_gdf, self.point_gdf)
        return self.process_flood_risk_result(flood_risk[['distance_m', 'flood_source', 'geometry']])

    def process_flood_risk_result(self, flood_risk):
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
        return output
    
    def run(self):
        self.output = []
        self.output.append(self.get_geological_disturbances())
        self.output.append(self.get_flood_risk())
        return self.output


if __name__ == '__main__':
    ef = EnvironmentalFeasibility([53.48433331, -1.576667], 5000, 123456)
    ef.run()
