"use client";

import {
  MapContainer,
  TileLayer,
  Marker,
  useMapEvents,
  Circle,
} from "react-leaflet";
import { useEffect } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useState } from "react";
import { Box, Typography } from "@mui/material";
import { Feature, Polygon, MultiPolygon, FeatureCollection } from "geojson";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";
import { point } from "@turf/helpers";

// Apply default marker
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

function LocationMarker({
  onSelect,
  radius,
  bound,
}: {
  onSelect: (coords: [number, number]) => void;
  radius: number;
  bound: FeatureCollection;
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
        alert("Please select a location within the UK.");
      }
    },
  });

  return position ? (
    <>
      <Marker position={position} />
      <Circle center={position} radius={radius} />
    </>
  ) : null;
}

export default function GeoMap({
  onLocationSelected,
  radius,
}: {
  onLocationSelected: (coords: [number, number]) => void;
  radius: number;
}) {
  const [UKBound, setUKBound] = useState<FeatureCollection | null>(null);

  useEffect(() => {
    fetch("/geojson/uk.geo.json")
      .then((res) => res.json())
      .then((data) => {
        setUKBound(data);
        console.log(data);
      });
  }, []);

  return (
    <Box sx={{ height: "400px", borderRadius: 2, overflow: "hidden", mt: 3 }}>
      {UKBound != null ? (
        <MapContainer
          center={{ lat: 53.505, lng: -0.09 }}
          zoom={6}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          <LocationMarker
            onSelect={onLocationSelected}
            radius={radius}
            bound={UKBound}
          />
        </MapContainer>
      ) : (
        <Typography>Loading boundaries...</Typography>
      )}
    </Box>
  );
}
