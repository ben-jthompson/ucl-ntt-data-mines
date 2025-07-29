import { FeatureCollection } from "geojson";
import axios from "axios";
import { FeatureLayer } from "@/types/FeatureLayer";

export function addLayer({
  layerPath,
  layerName,
  layerDescription,
  setLayers,
  setLayer,
}: {
  layerPath: string;
  layerName: string;
  layerDescription: string;
  setLayers: React.Dispatch<React.SetStateAction<FeatureLayer[] | null>>;
  setLayer: React.Dispatch<React.SetStateAction<FeatureCollection | null>>;
}): void {
  axios
    .get(`http://localhost:8080/api/geojson/${layerPath}`)
    .then((res) => {
      const geojson = res.data as FeatureCollection;

      setLayer(geojson);
      console.log(layerName, ": ", geojson);

      const newLayer: FeatureLayer = {
        layer: layerName,
        features: geojson,
        description: layerDescription,
      };

      setLayers((prevLayers) => [...(prevLayers ?? []), newLayer]);
    })
    .catch((err) => console.error("Failed to load layer:", err));
}
