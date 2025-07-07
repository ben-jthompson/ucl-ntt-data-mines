"use client";

import { Box, Grid, Typography } from "@mui/material";
import { MapContainer, TileLayer, Marker, Circle, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { stringify } from "querystring";

// Apply default marker
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

function LocationMarker({
  coords,
  radius,
}: {
  coords: [number, number] | null;
  radius: number;
}) {
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

export default function ResultMap({
  coords,
  radius,
  result,
}: {
  coords: [number, number] | null;
  radius: number;
  result: boolean;
}) {
  const zoomScale: { [key: number]: number } = {
    5000: 12,
    10000: 11,
    20000: 10,
  };

  const zoom = result ? (zoomScale[radius] ?? 7) - 1 : zoomScale[radius] ?? 6;

  return coords ? (
    <Box
      sx={{
        height: "400px",
        borderRadius: 2,
        overflow: "hidden",
        mt: 3,
        textAlign: "center",
      }}
    >
      <MapContainer
        center={{ lat: coords[0], lng: coords[1] }}
        zoom={zoom}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <LocationMarker coords={coords} radius={radius} />
      </MapContainer>
    </Box>
  ) : (
    <Grid
      container
      justifyContent="center"
      alignItems="center"
      style={{ minHeight: "100vh" }}
    >
      <Typography>
        An unexpected error occurred. Please reload the page.
      </Typography>
    </Grid>
  );
}
