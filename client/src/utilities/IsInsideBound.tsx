import { Feature, Polygon, MultiPolygon, FeatureCollection } from "geojson";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";
import { point } from "@turf/helpers";

export function isInsideBound({
  coords,
  bound,
}: {
  coords: [number, number];
  bound: FeatureCollection | null;
}) {
  if (!bound) return;
  console.log(coords);
  const marker = point([coords[1], coords[0]]);
  return bound.features.some((feature) => {
    if (
      feature.geometry.type === "Polygon" ||
      feature.geometry.type === "MultiPolygon"
    ) {
      return booleanPointInPolygon(
        marker,
        feature as Feature<Polygon | MultiPolygon>
      );
    }
    return false;
  });
}
