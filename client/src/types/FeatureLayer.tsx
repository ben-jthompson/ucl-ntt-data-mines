import { FeatureCollection } from "geojson";

export type FeatureLayer = {
  layer?: string;
  features?: FeatureCollection;
  description?: string;
};
