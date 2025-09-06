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
} from "react-leaflet";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Box, Button, Typography } from "@mui/material";
import { FeatureCollection } from "geojson";
import axios from "axios";
import { FeatureLayer } from "../types/FeatureLayer";
import { addLayer } from "@/utilities/AddLayer";
import { isInsideBound } from "@/utilities/IsInsideBound";

// Apply default marker
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
    const legend = new L.Control({ position: "topright" });

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
            .filter(([, isVisible]) => isVisible)
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
  }, [map, layers, layerLegend]);

  return null;
}

function LocationMarker({
  coords,
  onSelect,
  radius,
  bound,
  UK,
}: {
  coords: [number, number] | null;
  onSelect: (coords: [number, number]) => void;
  radius: number;
  bound: FeatureCollection | null;
  UK: FeatureCollection | null;
}) {
  useMapEvents({
    click(e: L.LeafletMouseEvent) {
      if (!bound) return;
      const pt: [number, number] = [e.latlng.lat, e.latlng.lng];
      if (
        isInsideBound({ coords: pt, bound }) &&
        isInsideBound({ coords: pt, bound: UK })
      ) {
        onSelect(pt);
      } else {
        alert(
          "Please select a location within mine extent, and within the bounds of UK land."
        );
      }
    },
  });

  return coords ? (
    <>
      <Marker position={coords}>
        <Popup>
          lat: {Math.round(coords[0] * 10000) / 10000}; lng:{" "}
          {Math.round(coords[1] * 10000) / 10000}
        </Popup>
      </Marker>
      <Circle center={coords} radius={radius} />
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
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
      }}
    >
      <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
        Layers (Click to toggle)
      </Typography>
      {Object.keys(visibility).map((name) => (
        <Button
          key={name}
          onClick={() => toggleLayer(name)}
          variant={visibility[name] ? "contained" : "outlined"}
          color={visibility[name] ? "primary" : "inherit"}
          size="small"
          sx={{ m: 0.5 }}
        >
          {formatLayerName(name)}
        </Button>
      ))}
    </Box>
  );
}

function formatLayerName(name: string): string {
  // Insert a space before each capital letter and capitalize first letter
  return name
    .replace(/([A-Z])/g, " $1") // insert space before caps
    .replace(/^./, (s) => s.toUpperCase()); // capitalize first char
}

export default function GeoMap({
  coords,
  onLocationSelected,
  radius,
}: {
  coords: [number, number] | null;
  onLocationSelected: (coords: [number, number]) => void;
  radius: number;
}) {
  const [, setLayers] = useState<FeatureLayer[] | null>(null);
  const [UKBound, setUKBound] = useState<FeatureCollection | null>(null);
  const [mineExtent, setMineExtent] = useState<FeatureCollection | null>(null);
  const [floodRisk, setFloodRisk] = useState<FeatureCollection | null>(null);
  const [layerVisibility, setLayerVisibility] = useState<
    Record<string, boolean>
  >({
    mineExtent: true,
    floodRisk: false,
  });
  const layerLegend: Record<string, string> = {
    mineExtent: `<i style="background: orange; width: 12px; height: 12px; display: inline-block; margin-right: 4px;"></i> Mine Extent<br/>`,
    floodRisk: `<i style="background: blue; width: 12px; height: 12px; display: inline-block; margin-right: 4px;"></i> Flood Risk<br/>`,
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
      layerPath: "Flood_Risk_Areas.json",
      layerName: "Designated high risk flood areas",
      layerDescription: "Shows high flood risk zones in the UK.",
      setLayers: setLayers,
      setLayer: setFloodRisk,
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
              coords={coords}
              onSelect={onLocationSelected}
              radius={radius}
              bound={mineExtent}
              UK={UKBound}
            />

            <LegendControl layers={layerVisibility} layerLegend={layerLegend} />

            {/* layer showing mine extent */}
            {layerVisibility.mineExtent && mineExtent && (
              <GeoJSON
                data={mineExtent}
                style={(): L.PathOptions => ({
                  color: "orange",
                  weight: 0.5,
                  fillOpacity: 0.3,
                })}
              />
            )}
            {/* layer showing floodrisk */}
            {layerVisibility.floodRisk && floodRisk && (
              <GeoJSON
                data={floodRisk}
                style={(): L.PathOptions => ({
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
