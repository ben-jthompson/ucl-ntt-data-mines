import geopandas as gpd
import pandas as pd
import random
import numpy as np
import os
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import contextily as ctx
import datetime as dt
from pyproj import Transformer
from shapely.geometry import Point
from .data_pipeline_funcs import find_and_sort_features, read_and_convert_geojson_file, find_average_depth, find_geometry_area, sample_features, remove_duplicate_features, convert_point_to_coords, calculation_mine_water
from ..formatting_graph.formatter_utils import file_format_string

class MineFeasibility:
    def __init__(self, coords, buffer, client_id):
        self.coords = coords
        self.point = Point(coords[1], coords[0])
        self.client_id = client_id
        self.buffer = buffer
        self.point_gdf = gpd.GeoDataFrame(geometry=[self.point], crs='EPSG:4326').to_crs('EPSG:27700')
        self.buffered_gdf = gpd.GeoDataFrame(
            geometry=self.point_gdf.buffer(float(buffer)),
            crs=self.point_gdf.crs
        )
        self.output = []

    #TODO: https://www.gov.uk/guidance/coal-mining-records-data-deeds-and-documents - summarise
    #TODO: USE FOR HELP: https://www.gov.uk/government/publications/apply-to-license-coal-mining-data/available-coal-mining-data-sets 
    #TODO: Ten Cities document - look at good criteria 
    # TODO: Check if workings are flooded? eg workings below groundwater
    # TODO: Check if area is probable working - add caveat, as mines mined longer ago are harder to georeference
    # TODO: Use probable workings as proxy for depth DEPTH	
    # TODO: Find overlapping workings via sampling
    # Depth

    # This is a depth statement of shallow, moderate or considerable, reflecting the likely depth of the probable working.

    # Shallow equals 0 to 30 metres below surface.

    # Moderate equals 30 to 100 metres below surface.

    # Considerable equals 100 plus metres below surface.
    #TODO: Check if area has future license - if so, find the nearest unlicensed area - then conduct analysis for that??? as in shift coords?
    # TODO: future license may have been revoked - check (https://www.gov.uk/government/publications/coal-mining-data-licence-areas/licence-areas-data-set-user-guide)
    def get_nearby_workings(self):
        probable_workings_mapping = {
            'Shallow': random.randint(0, 30),
            'Moderate': random.randint(30, 100),
            'Considerable': random.randint(100, 300)
        }

        underground_workings_map = read_and_convert_geojson_file('data/geojson/underground-workings-27700.geojson')
        probable_workings_map = read_and_convert_geojson_file('data/geojson/probable-workings.geojson')
        underground_workings = find_and_sort_features(underground_workings_map, self.buffered_gdf, self.point_gdf)            
        probable_workings = find_and_sort_features(probable_workings_map, self.buffered_gdf, self.point_gdf)
        underground_workings.drop('index_right', axis=1, inplace=True)
        probable_workings.drop('index_right', axis=1, inplace=True)
        underground_workings['depth'] = underground_workings['geometry'].apply(find_average_depth)
        underground_workings['area'] = underground_workings['geometry'].apply(find_geometry_area)
        spacing = self.buffer/5
        self.candidates = sample_features(feature_gdf=underground_workings, buffer_gdf=self.buffered_gdf, spacing=spacing)
        for idx, candidate in enumerate(self.candidates):
            if len(candidate['features']) < 2 or candidate['features']['depth'].mean() > -100:
                # look for probable workings if not enough documented workings
                buffered_point_gdf = gpd.GeoDataFrame(
                geometry=candidate['point'].buffer(float(50)),
                crs=candidate['point'].crs
            )
                filtered_probable_workings = find_and_sort_features(probable_workings, buffered_point_gdf, candidate['point'])
                filtered_probable_workings['area'] = filtered_probable_workings['geometry'].apply(find_geometry_area)
                if len(filtered_probable_workings) == 1 and filtered_probable_workings.iloc[0]['distance_m']>100:
                    continue
                else:
                    df = []
                    for _, row in filtered_probable_workings.iterrows():
                        df.append(pd.Series({'type':'Probable', 'depth': probable_workings_mapping[row['depth']], 'area': row['area'], 'distance_m': row['distance_m']}))
                        self.candidates[idx]['features'] = pd.concat([self.candidates[idx]['features'], pd.DataFrame(df)], ignore_index=True)
                        self.candidates[idx]['features'] = remove_duplicate_features(self.candidates[idx]['features'])
                        # print("Added probable workings (+ ", len(filtered_probable_workings), ")")
                        # print("Probable working areas derived from knowledge of areas which were being mined before or around 1872. Data has been estimated from available mining records by qualified mining surveyors.")
        self.derive_mine_working_ranks()
        now = str(dt.datetime.now())
        image_dir = os.path.join(os.getcwd(), 'server/uploads', str(self.client_id), 'report')
        os.makedirs(image_dir, exist_ok=True)
        self.image_path = os.path.join(image_dir, file_format_string(f'mine_img{now}'))
        self.produce_mine_image()   
        self.output.append(self.render_mining_text())
#

    def derive_mine_working_ranks(self):
        def calculate_score(candidate, temp_grad):
        # TODO: if only working above water level is probable working, then caution
        # TODO: calculate range, min, max, energy differential via temperature coalfields
            if not candidate:
                return 0, 'No features present'
            notes = []
            probables = len(candidate['features'][candidate['features']['type']=='Probable'])
            non_probables = len(candidate['features'][candidate['features']['type']!='Probable'])
            non_prob_min = []
            prob_min = []
            if non_probables > 0:
                non_prob_mean = candidate['features'][candidate['features']['type']!='Probable']['depth'].mean()
                non_prob_min = candidate['features'][candidate['features']['type']!='Probable']['depth'].nlargest(2).to_list()
            if probables > 0:
                prob_min = candidate['features'][candidate['features']['type']=='Probable']['depth'].nlargest(2).to_list()
            total = len(candidate['features'])
            if total == 0: 
                return 0, 'No features present'
            probables_ratio = probables/total
            if probables > 0:
                notes.append("DISCLAIMER: Probable working areas derived from knowledge of areas which were being mined before or around 1872. Data has been estimated from available mining records by qualified mining surveyors.")
            if probables == 0:
                notes.append('There are overlapping, recorded workings.')
                workings = 100
            elif total - probables >= 5:
                notes.append(f'There are multiple, overlapping, recorded workings - however, they are worked at an average of {-non_prob_mean}m below ground, which can pose problems for drilling and setting up data centres.')
                workings = 60
            elif probables_ratio > 0.5:
                notes.append(f"Most data of workings is unverified - they are likely present, but depth values are estimated and further surveying would be required.")
                workings = 40
            else:
                distances = [dist for dist in candidate['features']['distance_m']]
                if min(distances) < 50:
                    notes.append(f"There are few workings identified or expected in the area - nearest distance is {min(distances)}m")
                    workings = 10
                else:
                    notes.append(f"There are only a few workings identified or expected in the area - nearest distance is {min(distances)}")
                    workings = 20

            if not temp_grad.get('Type'):
                notes.append("Caution: mine water temperature data is unknown for this region. Calculations have been produced via average water temperature calculations, and will need to be verified.")
            if non_prob_min and len(non_prob_min)>1:
                depth_str = int(np.round(non_prob_min[1] / 100.0) * 100)
                depth_str = str(depth_str) if depth_str < -100 else "-100"
                temp = f"T{depth_str[1:]}m_Equi"
                temperature = temp_grad[temp]
                mine_water_calc_non_prob = calculation_mine_water(Q_watts=595000, T_source_C=temperature, lift_m=abs(non_prob_min[1]-non_prob_min[0]))
                if mine_water_calc_non_prob['feasible'] == False:
                    notes.append(mine_water_calc_non_prob['notes'])
                    workings = 0
                else: 
                    notes.append(f"For a 500kW data centre with 595kW of cooling demand, siting data centre at working at {abs(np.round(non_prob_min[0], 2))}m below ground level would require {np.round(mine_water_calc_non_prob['vol_flow_l_s'], 2)} litres per second to be pumped via a heat exchanger. Groundwater data is not available, but, assuming the confirmed nearest working at {abs(np.round(non_prob_min[1], 2))}m is flooded, the energy required to pump the water for heat exchange would be {np.round(mine_water_calc_non_prob['pump_power_kW'], 1)}kW.")

                    workings-=(mine_water_calc_non_prob['vol_flow_l_s']+mine_water_calc_non_prob['pump_power_kW'])
                    if min(non_prob_min) > 100:
                        workings-=abs(min(non_prob_min)/10)
            elif prob_min and len(prob_min)>1:
                depth_str = int(np.round(prob_min[1] / 100.0) * 100)
                depth_str = str(depth_str) if depth_str < -100 else "-100"
                temp = f"T{depth_str[1:]}m_Equi"
                temperature = temp_grad[temp]
                mine_water_calc_prob = calculation_mine_water(Q_watts=595000, T_source_C=temperature, lift_m=abs(prob_min[1]-prob_min[0]))
                if mine_water_calc_prob['feasible'] == False:
                    notes.append(mine_water_calc_prob['notes'])
                    workings *= 0
                else:
                    notes.append(f"For a 500kW data centre with 595kW of cooling demand, siting data centre at working at {abs(np.round(prob_min[0], 2))}m below ground level would require {np.round(mine_water_calc_prob['vol_flow_l_s'], 2)} litres per second to be pumped via a heat exchanger. However, groundwater data is not available, meaning that knowing whether workings are flooded or not requires more data; also as the working is not explicitly georeferenced, the depth value is indicative - but mine water temperatures and energy calculations should be similar.")
                    workings-=(mine_water_calc_prob['vol_flow_l_s']+mine_water_calc_prob['pump_power_kW'])
                    workings*=0.9
                    if min(prob_min) > 100:
                        workings-=abs(min(prob_min)/10)
            elif len(prob_min) == 1 and len(non_prob_min) == 1:
                vals = [prob_min[0], non_prob_min[0]]
                depth_str = int(np.round(max(vals) / 100.0) * 100)
                depth_str = str(depth_str) if depth_str < -100 else "-100"
                temp = f"T{depth_str[1:]}m_Equi"
                temperature = temp_grad[temp]
                mine_water_calc = calculation_mine_water(Q_watts=595000, T_source_C=temperature, lift_m=abs(max(vals)-min(vals)))
                if mine_water_calc['feasible'] == False:
                    notes.append(mine_water_calc['notes'])
                    workings = 0
                else:
                    notes.append(f"For a 500kW data centre with 595kW of cooling demand, siting data centre at working at {abs(np.round(max(vals), 2))}m below ground level would require {np.round(mine_water_calc['vol_flow_l_s'], 2)} litres per second to be pumped via a heat exchanger. However, groundwater data is not available, meaning that knowing whether workings are flooded or not requires more data; also as one of the workings is not explicitly georeferenced, the depth value may be indicative - but mine water temperatures and energy calculations should be similar.")
                    workings-=(mine_water_calc['vol_flow_l_s']+mine_water_calc['pump_power_kW'])
                    if min(vals) > 100:
                        workings-=abs(min(vals)/10)
                    workings*=0.95
            elif non_prob_min == None and prob_min == None:
                notes.append("No mine features found under this specific point.")
                workings=0
            else:
                val1 = prob_min[0] if prob_min and len(prob_min) > 0 else None
                val2 = non_prob_min[0] if non_prob_min and len(non_prob_min) > 0 else None

                # Only consider the non-None values
                vals = [v for v in [val1, val2] if v is not None]
                depth_str = int(np.round(vals[0] / 100.0) * 100)
                depth_str = str(depth_str) if depth_str < -100 else "-100"
                temp = f"T{depth_str[1:]}m_Equi"
                temperature = temp_grad[temp]
                mine_water_calc = calculation_mine_water(Q_watts=595000, T_source_C=temperature, lift_m=0)
                
                notes.append(f"Only one working found beneath this point, at {-(np.round(vals[0]))}m below ground level.")
                workings=0
            # TODO: CAP AT 0!
            
            workings = max(workings, 0)
            return workings, notes
        self.max_score = 0 
        self.all_scores = []
        temp_grad_map = read_and_convert_geojson_file('data/geojson/coalfield-temperature-gradients.geojson')
        temp_grad = find_and_sort_features(temp_grad_map, self.buffered_gdf, self.point_gdf)
        row_found = None
        for i, (_, row) in enumerate(temp_grad.iterrows()):
            if row['Equilibr_1'] != 'No_Data':
                row_found = row
                break
            if i == len(temp_grad) - 1: 
                row_found = { "properties":{"Equilibriu": "Yes", "Equilibr_1": "Measured", "T100m_Equi": 11.7, "T100m_Eq_1": 0.0, "T100m_Eq_2": 0.0, "T200m_Equi": 13.6, "T200m_Eq_1": 0.0, "T200m_Eq_2": 0.0, "T300m_Equi": 15.4, "T300m_Eq_1": 0.0, "T300m_Eq_2": 0.0, "T400m_Equi": 17.3, "T400m_Eq_1": 0.0, "T400m_Eq_2": 0.0, "T500m_Equi": 19.1, "T500m_Eq_1": 0.0, "T500m_Eq_2": 0.0, "T600m_Equi": 21.0, "T600m_Eq_1": 0.0, "T600m_Eq_2": 0.0, "T700m_Equi": 22.9, "T700m_Eq_1": 0.0, "T700m_Eq_2": 0.0, "T800m_Equi": 24.7, "T800m_Eq_1": 0.0, "T800m_Eq_2": 0.0, "T900m_Equi": 26.6, "T900m_Eq_1": 0.0, "T900m_Eq_2": 0.0, "T1000m_Equ": 28.5, "T1000m_E_1": 0.0, "T1000m_E_2": 0.0}}
        temp_grad = row_found


        for candidate in self.candidates:
            candidate['score'], candidate['notes'] = calculate_score(candidate, temp_grad)
            self.all_scores.append(candidate['score'])
            if candidate['score'] > self.max_score:
                self.max_score = candidate['score']

        
    def render_mining_text(self):
        average_score = round(sum(self.all_scores)/len(self.all_scores), 2)
        explanation = f'Over the highlighted area, the average suitability score based on mine features is {average_score}, '
        if average_score > 75:
            explanation += 'meaning that many mine formations in the area would be good for data centre placement - owing to many overlapping, verified features, which can facilitate mine water heat transfer and cooling operations. '
        elif average_score > 50:
            explanation += 'meaning that some mine formations in the area would be good for data centre placement - owing to overlapping features, which can facilitate mine water heat transfer and cooling operations. '
        elif average_score > 20:
            explanation += 'meaning that few mine formations in the area would be good for data centre placement - owing to overlapping features, which can facilitate mine water heat transfer and cooling operations. '
        else:
            explanation += 'meaning that there is little opportunity for data centre placement - many areas may have few, or no overlapping workings, limiting the potential for mine water heat transfer and cooling.'
        for candidate in self.candidates:
            if candidate['score'] == self.max_score:
                lat, lng = convert_point_to_coords(candidate['point'])
                cand_coords = (lat, lng)
                ew = 'east' if cand_coords[1] >= self.coords[1] else 'west'
                ns = 'north' if cand_coords[0] >= self.coords[0] else 'south'
                str_cand = [str(coord) for coord in cand_coords]
                explanation += f'The max suitability score across the sampled points (as seen on the figure below) was {np.round(self.max_score, 2)} - located in the {ns}{ew} quadrant, at {str_cand[0]}N, {str_cand[1]}E. Site choice explanation: {" ".join(candidate["notes"])}'
                return {'topic': 'Mine Workings Suitability', 'explanation': explanation, 'fig': [f"{self.image_path}.png", 'Mine Workings Suitability Map']}
        # else:
        #     while self.max_score[1] > 0:
        #         for candidate in self.candidates:
        #             if candidate['score'] == self.max_score:
        #                 explanation += f""

    def produce_mine_image(self):
        fig, ax = plt.subplots(figsize=(10, 10))
        
        points = []
        scores = []
        #TODO: FIX SCALE!

        for candidate in self.candidates:
            point = candidate["point"].geometry.iloc[0] 
            points.append(point)
            scores.append(candidate.get("score", 0))
        plot_gdf = gpd.GeoDataFrame(
            {"score": scores},
            geometry=points,
            crs=self.candidates[0]["point"].crs
        )
        plot_gdf = plot_gdf.to_crs(epsg=3857)
        plot_gdf_latlng = plot_gdf.to_crs(epsg=4326)
        plot_gdf["lng"] = plot_gdf_latlng.geometry.x
        plot_gdf["lat"] = plot_gdf_latlng.geometry.y
        plot_gdf.plot(
            ax=ax,
            column="score",
            marker="*",
            markersize=150,
            cmap="RdYlGn",
            legend=True,
            legend_kwds={'label': "Suitability Score", 'shrink': 0.6},
            edgecolor="black", 
            linewidth=0.8 
        )

        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

        lng_min, lat_min = transformer.transform(xmin, ymin)
        lng_max, lat_max = transformer.transform(xmax, ymax)

        # Update axis labels
        ax.set_xticks([xmin, xmax])
        ax.set_xticklabels([f"{lng_min:.2f}", f"{lng_max:.2f}"])

        ax.set_yticks([ymin, ymax])
        ax.set_yticklabels([f"{lat_min:.2f}", f"{lat_max:.2f}"])
        ctx.add_basemap(ax, crs='EPSG:3857', source=ctx.providers.Esri.WorldStreetMap, alpha=0.75)
        # ax.set_axis_off()
        plt.tight_layout()
        print("IMGPATH M: ", self.image_path)
        plt.savefig(self.image_path, dpi=300)
        plt.close(fig)
        return
    
    def get_licensed_areas(self):
        licenses_map = read_and_convert_geojson_file('data/geojson/license-areas.geojson')
        licenses = find_and_sort_features(licenses_map, self.buffered_gdf, self.point_gdf)
        licenses_responsibility_map = read_and_convert_geojson_file('data/geojson/license-area-of-responsibility.geojson')
        licenses_responsibility_areas = find_and_sort_features(licenses_responsibility_map, self.buffered_gdf, self.point_gdf)
        output = self.process_licensed_areas(licenses, licenses_responsibility_areas)
        output['explanation'] = 'The Coal Authority licenses the extraction of coal, including operations such as mining, exploration, and other coal-related activities. Licensed areas indicate that coal mining operations have been planned or undertaken since 1994 - however, there are plenty of coal workings existing that have remained unworked since 1994 and are thus recorded as having no license area - this, however, does not imply that a license is not required to operate. Statistics for your chosen area: ' + " ".join(output['explanation'])
        self.output.append(output)

    def process_licensed_areas(self, licenses, license_areas):
        if len(licenses) == 0 or (len(licenses) == 1 and licenses.iloc[0]['distance_m'] > self.buffer):
            if len(license_areas) == 1 and license_areas.iloc[0]['distance_m'] > self.buffer:
                return {'topic':"Licensed Areas", "explanation":["No areas within the search radius have been the subject of a license, granted or planned, since 1994."]}
            elif len(license_areas) >= 1:
                active_areas = [area for _, area in license_areas.iterrows() if area['l_status'] == 'Granted' and str(area['revoke_date']) == 'NaT']

                if active_areas:
                    if len(active_areas) == 1:
                        area = active_areas[0]
                        return {
                            'topic': 'Licensed Areas',
                            "explanation": ([
                                f"The area around the selected coordinate is partially within the area of responsibility "
                                f"from {area['l_name'].title()} – an {area['l_type'].lower()} working."
                            ])
                        }
                    else:
                        names = ", ".join(
                            f"{a['l_name'].title()} - {a['l_type']} working"
                            for a in active_areas
                        )
                        return {
                            'topic': 'Licensed Areas',
                            "explanation": ([
                                f"The area around the selected coordinate overlaps with multiple active licensed areas: {names}."
                            ])
                        }
                else:
                    return {
                        'topic': "Licensed Areas",
                        "explanation": ["No areas within the search radius are currently under license, but licenses have been issued for the area since 1994 (for more info visit https://datamine-cauk.hub.arcgis.com/)."]
                    }

        else:
            explanation = []
            for ind, license in licenses.iterrows():
                if license['status'] == "Past":
                    if license['l_status'] == 'Granted':
                        if str(license['revoke_date']) != 'NaT':
                            date_str = dt.datetime.fromisoformat(str(license['revoke_date']))
                            formatted = date_str.strftime("%d %B %Y")
                            explanation.append(f"License has formerly been granted in the area: {license['sitename'].title()} - license expired/revoked on {formatted}.")
                        else:
                            explanation.append(f"License has formerly been granted in the area: {license['sitename'].title()}.")
                    elif license['l_status'] == 'Withdrawn':
                        explanation.append(f"Since 1994, an application for {license['sitename'].title()} was granted - however, it has since been withdrawn.")
                    else:
                        if str(license['revoke_date']) != "NaT":
                            date_str = dt.datetime.fromisoformat(str(license['revoke_date']))
                            formatted = date_str.strftime("%d %B %Y")
                            explanation.append(f"A license has been granted in the past at {license['sitename'].title()} however, it was revoked on {formatted}.")
                        else:
                            explanation.append(f"A license has been granted in the past at {license['sitename'].title()}.")
                        
                elif license['status'] == "Current" and license['l_status'] == "Granted":
                    date_str = dt.datetime.fromisoformat(str(license['grant_date']))
                    formatted = date_str.strftime("%d %B %Y")
                    explanation.append(f"The area {license['sitename'].title()} - an {license['l_type'].lower()} mine - is currently licensed, having being granted on {formatted}.")
                elif license['status'] == "Current":
                    date_str = dt.datetime.fromisoformat(str(license['grant_date']))
                    formatted = date_str.strftime("%d %B %Y")
                    explanation.append(f"The area {license['sitename'].title()} previously had a license, but it was revoked on {formatted}")
                elif license['status'] == "Future" and license['l_status'] == "Application":
                    explanation.append(f"A license has been applied for for the area {license['sitename'].title()}")
                elif license['status'] == "Future" and license['l_status'] == "Granted":
                    explanation.append(f"A license has been granted for {license['sitename']} for future working, exploration or other coal-related activities.")
                elif license['status'] == 'Future' and license['l_status'] in ["Cancelled", "Withdrawn"]:
                    explanation.append(f"License was applied for for {license['sitename']}, but the application was later cancelled or withdrawn.")
                elif license['status'] == 'Future' and license['l_status']=='Revoked':
                           
                    date_str = dt.datetime.fromisoformat(str(license['grant_date']))
                    formatted_grant = date_str.strftime("%d %B %Y")
                    if str(license['revoke_date']) != 'NaT':
                        date_str = dt.datetime.fromisoformat(str(license['revoke_date']))
                        formatted_revoke = date_str.strftime("%d %B %Y")
                        explanation.append(f"License was granted for {license['sitename']} on {formatted_grant}, but was revoked on {formatted_revoke}.")
                    else:
                        explanation.append(f"License was granted for {license['sitename']} on {formatted_grant}, but was revoked.")
                else: 
                    explanation.append(f"Area not covered: {license['sitename']}")
            return {'topic': 'Licensed Areas', 'explanation': explanation}
        

    def identify_abandonment_plans(self):
        self.output.append({'topic': 'Relevant Mine Abandonment Plans', 'explanation': 'Relevant abandonment plans can be accessed by visiting the <a href="https://datamine-cauk.hub.arcgis.com/">Mining Remediation Authority Map Viewer</a>, navigating the "Abandoned Mines Catalogue" layer and locating your point of interest. You will find catalogue numbers which correspond to particular areas - these numbers can be requested from the Mining Remediation Authority and can cover historical mines plans, depicting areas of extraction and seam entry points (for more information, visit <a href="https://www.gov.uk/guidance/coal-mining-records-data-deeds-and-documents">https://www.gov.uk/guidance/coal-mining-records-data-deeds-and-documents</a>).'})

    def run(self):
        self.get_nearby_workings()
        self.get_licensed_areas()
        self.identify_abandonment_plans()
        return self.output

if __name__ == "__main__":
    ma = MineFeasibility([53.41, -2.15], 5000, 123455)
    ma.run()