"use client";

import {
  MapContainer,
  TileLayer,
  Marker,
  useMapEvents,
  Circle,
  Popup,
  GeoJSON,
  useMap,
  CircleMarker,
} from "react-leaflet";
import { useEffect, useMemo, useState } from "react";
import "leaflet/dist/leaflet.css";
import L, { PathOptions } from "leaflet";
import { Box, Typography } from "@mui/material";
import {
  GeoJsonObject,
  Feature,
  Polygon,
  MultiPolygon,
  FeatureCollection,
} from "geojson";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";
import { point } from "@turf/helpers";
import axios from "axios";
import { FeatureLayer } from "../types/FeatureLayer";
import { addLayer } from "@/utilities/AddLayer";
import MarkerClusterGroup from "react-leaflet-markercluster";

// Apply default marker
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

function LegendControl({
  layers,
  layerLegend,
}: {
  layers: Record<string, boolean> | null;
  layerLegend: Record<string, string>;
}) {
  const map = useMap();

  useEffect(() => {
    const legend = L.control({ position: "topright" });

    legend.onAdd = function () {
      const div = L.DomUtil.create("div", "info legend");

      div.innerHTML = `
      <div style="
        background: #f0f0f0;
        padding: 4px 10px;
        border-radius: 5px;
        font-size: 14px;
      ">
        <h4 style="margin: 0 0 4px 0;">Legend</h4>
        ${
          layers &&
          Object.entries(layers)
            .filter(([_, isVisible]) => isVisible)
            .map(([layerName]) => layerLegend[layerName] || "")
            .join("")
        }
      </div>
    `;

      return div;
    };

    legend.addTo(map);

    return () => {
      legend.remove();
    };
  }, [map, layers]);

  return null;
}

function LocationMarker({
  onSelect,
  radius,
  bound,
}: {
  onSelect: (coords: [number, number]) => void;
  radius: number;
  bound: FeatureCollection | null;
}) {
  const [position, setPosition] = useState<[number, number] | null>(null);
  useMapEvents({
    click(e: any) {
      if (!bound) return;
      const pt = point([e.latlng.lng, e.latlng.lat]); // note lng, lat order
      const isInsideAnyPolygon = bound.features.some((feature) => {
        if (
          feature.geometry.type === "Polygon" ||
          feature.geometry.type === "MultiPolygon"
        ) {
          return booleanPointInPolygon(
            pt,
            feature as Feature<Polygon | MultiPolygon>
          );
        }
        return false;
      });

      if (isInsideAnyPolygon) {
        const coords: [number, number] = [e.latlng.lat, e.latlng.lng];
        setPosition(coords);
        onSelect(coords);
      } else {
        alert("Please select a location within mine extent.");
      }
    },
  });

  return position ? (
    <>
      <Marker position={position}>
        <Popup>
          lat: {Math.round(position[0] * 10000) / 10000}; lng:{" "}
          {Math.round(position[1] * 10000) / 10000}
        </Popup>
      </Marker>
      <Circle center={position} radius={radius} />
    </>
  ) : null;
}

function LayerToggleBar({
  visibility,
  toggleLayer,
}: {
  visibility: Record<string, boolean>;
  toggleLayer: (name: string) => void;
}) {
  return (
    <div className="p-2 bg-gray-100 rounded shadow">
      <h4 className="text-sm font-bold mb-2">Layers</h4>
      {Object.keys(visibility).map((name) => (
        <button
          key={name}
          onClick={() => toggleLayer(name)}
          className={`px-2 py-1 m-1 rounded ${
            visibility[name] ? "bg-blue-500 text-white" : "bg-gray-300"
          }`}
        >
          {name}
        </button>
      ))}
    </div>
  );
}

// Memoize markers array
// const markers = useMemo(() => {
//   return mineEntries?.features.map((feature) => {
//     const coords = feature.geometry.coordinates;
//     return (
//       <CircleMarker
//         key={feature.properties?.id}
//         center={[coords[1], coords[0]]}
//       />
//     );
//   });
// }, [mineEntries]);

export default function GeoMap({
  onLocationSelected,
  radius,
}: {
  onLocationSelected: (coords: [number, number]) => void;
  radius: number;
}) {
  const [layers, setLayers] = useState<FeatureLayer[] | null>(null);
  const [UKBound, setUKBound] = useState<FeatureCollection | null>(null);
  const [mineExtent, setMineExtent] = useState<FeatureCollection | null>(null);
  const [mineEntries, setMineEntries] = useState<FeatureCollection | null>(
    null
  );
  const [aquifers, setAquifers] = useState<FeatureCollection | null>(null);
  const [UKGeology, setUKGeology] = useState<FeatureCollection | null>(null);
  const [layerVisibility, setLayerVisibility] = useState<
    Record<string, boolean>
  >({
    mineExtent: true,
    mineEntries: false,
    aquifers: true,
    wasteHeat: false,
  });
  const layerLegend: Record<string, string> = {
    mineExtent: `<i style="background: orange; width: 12px; height: 12px; display: inline-block; margin-right: 4px;"></i> Mine Extent<br/>`,
    mineEntries: `<i style="background: brown; width: 12px; height: 12px; display: inline-block; margin-right: 4px;"></i> Mine Entries<br/>`,
    aquifers: `<i style="background: blue; width: 12px; height: 12px; display: inline-block; margin-right: 4px;"></i> Aquifers<br/>`,
    wasteHeat: `<i style="background: red; width: 12px; height: 12px; display: inline-block; margin-right: 4px;"></i> Waste Heat Sites<br/>`,
  };

  // toggle layer visibility on/off
  const toggleLayer = (layer: string) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layer]: !prev[layer],
    }));
  };

  useEffect(() => {
    axios.get("geojson/uk.geo.json").then((res) => setUKBound(res.data));
  });

  useEffect(() => {
    addLayer({
      layerPath: "coalfield-extent-4326.geojson",
      layerName: "UK Mine Extent",
      layerDescription: "Shows the extent of existing mine workings in the UK.",
      setLayers: setLayers,
      setLayer: setMineExtent,
    });
  }, []);

  useEffect(() => {
    addLayer({
      layerPath: "mine-test.geojson",
      layerName: "UK Mine Entries",
      layerDescription:
        "Shows the location of mine entries (shafts, adits) in the UK.",
      setLayers: setLayers,
      setLayer: setMineEntries,
    });
  }, []);

  useEffect(() => {
    addLayer({
      layerPath: "aquifers-cropped-4326.geojson",
      layerName: "Aquifers under Mines",
      layerDescription:
        "Shows the groundwater resources lying below mines in the UK.",
      setLayers: setLayers,
      setLayer: setAquifers,
    });
  }, []);

  return (
    <>
      <LayerToggleBar visibility={layerVisibility} toggleLayer={toggleLayer} />
      <Box
        sx={{
          height: "400px",
          borderRadius: 2,
          overflow: "hidden",
          mt: 3,
          textAlign: "center",
        }}
      >
        {UKBound != null ? (
          <MapContainer
            center={{ lat: 53.505, lng: -0.09 }}
            zoom={6}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap"
            />

            <LocationMarker
              onSelect={onLocationSelected}
              radius={radius}
              bound={mineExtent}
            />

            <LegendControl layers={layerVisibility} layerLegend={layerLegend} />

            {/* layer showing mine extent */}
            {layerVisibility.mineExtent && mineExtent && (
              <GeoJSON
                data={mineExtent}
                style={(feature: Feature): PathOptions => ({
                  color: "orange",
                  weight: 0.5,
                  fillOpacity: 0.3,
                })}
              />
            )}
            {/* layer showing mine extent */}
            {layerVisibility.aquifers && aquifers && (
              <GeoJSON
                data={aquifers}
                style={(feature: Feature): PathOptions => ({
                  color: "blue",
                  weight: 0.5,
                  fillOpacity: 0.3,
                })}
              />
            )}
          </MapContainer>
        ) : (
          <Typography>Loading boundaries...</Typography>
        )}
      </Box>
    </>
  );
}
